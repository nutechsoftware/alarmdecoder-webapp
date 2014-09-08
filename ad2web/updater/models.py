import os
import sys

import sh
import sqlalchemy.exc
from sqlalchemy import create_engine, pool
from alembic import command
from alembic.migration import MigrationContext
from alembic.config import Config
from alembic.script import ScriptDirectory
from flask import current_app

class Updater(object):
    """
    The primary update system
    """
    def __init__(self):
        """
        Constructor
        """
        self._components = {}

        self._components['webapp'] = SourceUpdater('webapp')

    def check_updates(self):
        """
        Performs a check for component updates

        :returns: A list of components and their statuses.
        """
        status = {}

        for name, component in self._components.iteritems():
            component.refresh()
            status[name] = (component.needs_update, component.branch, component.local_revision, component.remote_revision, component.status)

        return status

    def update(self, component_name=None):
        """
        Updates the specificed component or all components.

        :param component_name: Name of the component to update.
        :type component_name: string

        :returns: A list of components and the status after the update.
        """
        ret = {}

        if component_name is not None:
            component = self._components[component_name]

            ret[component_name] = component.update()
        else:
            for name, component in self._components.iteritems():
                if component.needs_update():
                    ret[component_name] = component.update()

        return ret

class SourceUpdater(object):
    """
    Git-based update system
    """

    def __init__(self, name):
        """
        Constructor

        :param name: Name of the component
        :type name: string
        """
        try:
            self._git = sh.git
        except sh.CommandNotFound:
            self._git = None

        self.name = name
        self._branch = ''
        self._local_revision = None
        self._remote_revision = None
        self._commits_ahead = 0
        self._commits_behind = 0
        self._enabled, self._status = self._check_enabled()

        self._db_updater = DBUpdater()
        self._requirements_updater = RequirementsUpdater()

    @property
    def branch(self):
        """Returns the current branch"""
        return self._branch

    @property
    def local_revision(self):
        """Returns the current local revision"""
        return self._local_revision

    @property
    def remote_revision(self):
        """Returns the current remote revision"""
        return self._remote_revision

    @property
    def commit_count(self):
        """Returns the number of commits behind and ahead of the remote branch"""
        return self._commits_behind, self._commits_ahead

    @property
    def status(self):
        """Returns the status string"""
        return self._status

    @property
    def needs_update(self):
        """Determines if a component needs an update"""
        if self._enabled:
            behind, ahead = self.commit_count

            if behind is not None and behind > 0:
                return True

        return False

    def refresh(self):
        """
        Refreshes the component status
        """
        self._update_status()

        if not self._enabled:
            return

        self._fetch()

        self._retrieve_branch()
        self._retrieve_local_revision()
        self._retrieve_remote_revision()
        self._retrieve_commit_count()

        self._requirements_updater.refresh()
        self._db_updater.refresh()

    def update(self):
        """
        Performs the update

        :returns: Returns the update results
        """
        if not self._enabled:
            return { 'status': 'FAIL', 'restart_required': False }

        try:
            results = self._git.merge('origin/{0}'.format(self.branch))

            self._requirements_updater.update()
            self._db_updater.update()
        except sh.ErrorReturnCode, err:
            return { 'status': 'FAIL', 'restart_required': False }

        return { 'status': 'PASS', 'restart_required': True }

    def _retrieve_commit_count(self):
        """
        Retrieves the commit counts
        """
        try:
            results = self._git('rev-list', '@{upstream}...HEAD', left_right=True).strip()

            self._commits_behind, self._commits_ahead = results.count('<'), results.count('>')
            self._update_status()
        except sh.ErrorReturnCode:
            self._commits_behind, self._commits_ahead = 0, 0

    def _retrieve_branch(self):
        """
        Retrieves the current branch
        """
        try:
            results = self._git('symbolic-ref', 'HEAD', q=True).strip()
            self._branch = results.replace('refs/heads/', '')
        except sh.ErrorReturnCode:
            self._branch = ''

    def _retrieve_local_revision(self):
        """
        Retrieves the current local revision
        """
        try:
            self._local_revision = self._git('rev-parse', 'HEAD').strip()
        except sh.ErrorReturnCode:
            self._local_revision = None

    def _retrieve_remote_revision(self):
        """
        Retrieves the current remote revision
        """
        results = None

        try:
            results = self._git('rev-parse', '--verify', '--quiet', '@{upstream}').strip()

            if results == '':
                results = None
        except sh.ErrorReturnCode:
            pass

        self._remote_revision = results

    def _fetch(self):
        """
        Performs a fetch from the origin
        """
        try:
            # HACK:
            #
            # Ran into an issue when trying to fetch from an ssh-based
            # repository and need a good way to make sure that fetch doesn't
            # forever block while asking for an ssh password.  _bg didn't do
            # the job but a combination of _iter and _timeout seems to work
            # fine.
            #
            for c in self._git.fetch('origin', _iter_noblock=True, _timeout=30):
                pass

        except sh.ErrorReturnCode:
            pass

    def _update_status(self, status=''):
        """
        Updates the status string
        """
        self._status = status

        enabled, enabled_status = self._check_enabled()

        if not enabled:
            self._status = enabled_status
        else:
            temp_status = []
            if self._commits_behind is not None and self._commits_behind > 0:
                temp_status.append('{0} commit{1} behind'.format(self._commits_behind, '' if self._commits_behind == 1 else 's'))

            if self._commits_ahead is not None and self._commits_ahead > 0:
                temp_status.append('{0} commit{1} ahead'.format(self._commits_ahead, '' if self._commits_ahead == 1 else 's'))

            if len(temp_status) == 0:
                self._status = 'Up to date!'
            else:
                self._status += ', '.join(temp_status)

    def _check_enabled(self):
        """
        Determine if this update component is enabled

        :returns: Whether or not this component is enabled.
        """
        git_available = self._git is not None
        remote_okay = self._check_remotes()

        status = ''
        if not git_available:
            status = 'Disabled (Git is unavailable)'

        if not remote_okay:
            status = 'Disabled (SSH origin)'

        return (git_available and remote_okay, status)

    def _check_remotes(self):
        """
        Hack of a check determine if our origin remote is via ssh since it
        blocks if the key has a password.

        :returns: Whether or not we're running with an ssh remote.
        """
        if not self._git:
            return True

        try:
            remotes = self._git.remote(v=True)
            for r in remotes.strip().split("\n"):
                name, path = r.split("\t")
                if name == 'origin' and '@' in path:
                    return False
        except sh.ErrorReturnCode_128:
                return False

        return True


class DBUpdater(object):
    """
    Database update system
    """

    def __init__(self):
        """
        Constructor
        """
        self._config = Config()
        self._config.set_main_option("script_location", "alembic")

        self._script = ScriptDirectory.from_config(self._config)
        self._engine = create_engine(current_app.config.get('SQLALCHEMY_DATABASE_URI'))

    @property
    def needs_update(self):
        """Returns whether or not the component needs an update"""
        if self.current_revision != self.newest_revision:
            return True

        return False

    @property
    def current_revision(self):
        """Returns the current database revision"""
        return self._current_revision

    @property
    def newest_revision(self):
        """Returns the newest revision available"""
        return self._newest_revision

    @property
    def status(self):
        """Returns the component status"""
        return ''

    def refresh(self):
        """
        Refreshes the component status
        """
        self._open()

        self._current_revision = self._context.get_current_revision()
        self._newest_revision = self._script.get_current_head()

        self._close()

    def update(self):
        """
        Performs the update

        :returns: The update results
        """
        if self._current_revision != self._newest_revision:
            try:
                command.upgrade(self._config, 'head')
            except sqlalchemy.exc.OperationalError, err:
                return False

        return True

    def _open(self):
        """
        Create a connection and migration _context
        """
        self._connection = self._engine.connect()
        self._context = MigrationContext.configure(self._connection)

    def _close(self):
        """
        Closes down the connection
        """
        self._connection.close()
        self._connection = self._context = None


class RequirementsUpdater(object):
    def __init__(self):
        self.local_options = self._get_local_options()
        self.finder = self._get_package_finder()
        self.requirement_list = []

    def refresh(self):
        return self._check_requirements()

    def needs_update(self):
        return bool(self.requirements_needed)

    def update(self):
        for r in self.requirements_needed:
            self._install_requirement(r)

        return True

    def _install_requirement(self, requirement):
        if not local_options:
            local_options = []

        if self._check_requirement(requirement):
            return True

        try:
            # Parse requirement
            requirement = InstallRequirement.from_line(str(requirement), None)

            # Build the requirement set.  We're doing this one at a time so we can actually detect
            # which ones fail.
            requirement_set = RequirementSet(build_dir=build_prefix, src_dir=src_prefix, download_dir=None)        
            requirement_set.add_requirement(requirement)

        try:
            # Download and build requirement
            try:
                requirement_set.prepare_files(package_finder, force_root_egg_info=False, bundle=False)
            except PreviousBuildDirError, err:
                # Remove previous build directories if they're detected.. shouldn't be an issue
                # now that we've removed upstream dependencies from requirements.txt.
                import shutil
                location = requirement.build_location(build_prefix, True)

                shutil.rmtree(location)
                requirement_set.prepare_files(package_finder, force_root_egg_info=False, bundle=False)

            # Finally, install the requirement.
            requirement_set.install(local_options, [])

        except Exception, err:
            return False

        return True

    def _check_requirements(self):
        # TODO: Fix hardcoded path
        self.requirement_list = [r.strip() for r in open('requirements.txt').readlines()]
        self.requirements_needed = [r for r in self.requirement_list if self._check_requirement(r)]

        return bool(self.requirements_needed)

    def _check_requirement(self, requirement):
        dist = None
        try:
            dist = working_set.find(Requirement.parse(requirement))
        except ValueError, err:
            pass

        return dist

    def _get_local_options(self):
        local_options = []
        # Force install into the user directory if this isn't a virtualenv and we're not root.
        if not hasattr(sys, 'real_prefix') and not os.geteuid() == 0:
            local_options.append('--user')

        return local_options

    def _get_package_finder(self):
        finder_options = {
            'find_links': [],
            'index_urls': ['http://pypi.python.org/simple/'],
        }

        # Handle pip 1.5 deprecating dependency_links and force it to process them for alarmdecoder/pyftdi.
        try:
            from pip.cmdoptions import process_dependency_links
            finder_options['process_dependency_links'] = True
        except ImportError:
            pass

        # Create package finder to search for packages for us.
        return PackageFinder(**finder_options)
