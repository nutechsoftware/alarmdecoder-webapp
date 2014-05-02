import sh
import sqlalchemy.exc
from sqlalchemy import create_engine, pool
from alembic import command
from alembic.migration import MigrationContext
from alembic.config import Config
from alembic.script import ScriptDirectory
from flask import current_app

class Updater(object):
    def __init__(self):
        self._components = {}

        self._components['webapp'] = SourceUpdater('webapp')

    def check_updates(self):
        status = {}

        for name, component in self._components.iteritems():
            component.refresh()
            status[name] = (component.needs_update, component.branch, component.local_revision, component.remote_revision, component.status)

        return status

    def update(self, component_name=None):
        ret = { }

        if component_name is not None:
            component = self._components[component_name]

            ret[component_name] = component.update()
        else:
            for name, component in self._components.iteritems():
                if component.needs_update():
                    ret[component_name] = component.update()

        return ret


class SourceUpdater(object):
    def __init__(self, name):
        try:
            self._git = sh.git
        except sh.CommandNotFound:
            self._git = None

        self.name = name
        self._branch = 'master'
        self._local_revision = None
        self._remote_revision = None
        self._commits_ahead = 0
        self._commits_behind = 0
        self._enabled, self._status = self._check_enabled()

        self._db_updater = DBUpdater()

    @property
    def branch(self):
        return self._branch

    @property
    def local_revision(self):
        return self._local_revision

    @property
    def remote_revision(self):
        return self._remote_revision

    @property
    def commit_count(self):
        return self._commits_behind, self._commits_ahead

    @property
    def status(self):
        return self._status

    @property
    def needs_update(self):
        if self._enabled:
            behind, ahead = self.commit_count

            if behind is not None and behind > 0:
                return True

        return False

    def refresh(self):
        self._update_status()

        if not self._enabled:
            return

        self._fetch()

        self._retrieve_branch()
        self._retrieve_local_revision()
        self._retrieve_remote_revision()
        self._retrieve_commit_count()

        self._db_updater.refresh()

    def update(self, branch=None):
        if not self._enabled:
            return { 'status': 'FAIL', 'restart_required': False }

        try:
            #results = self._git.merge('origin/{0}'.format(self.branch()))

            self._db_updater.update()
        except sh.ErrorReturnCode, err:
            # error
            pass

        return { 'status': 'PASS', 'restart_required': True }

    def _retrieve_commit_count(self):
        try:
            results = self._git('rev-list', '@{upstream}...HEAD', left_right=True).strip()

            self._commits_behind, self._commits_ahead = results.count('<'), results.count('>')
            self._update_status()
        except sh.ErrorReturnCode:
            pass

    def _retrieve_branch(self):
        try:
            results = self._git('symbolic-ref', 'HEAD', q=True).strip()
            self._branch = results.replace('refs/heads/', '')
        except sh.ErrorReturnCode:
            pass

    def _retrieve_local_revision(self):
        try:
            results = self._git('rev-parse', 'HEAD')

            self._local_revision = results.strip()
        except sh.ErrorReturnCode:
            pass

    def _retrieve_remote_revision(self):
        results = None

        try:
            results = self._git('rev-parse', '--verify', '--quiet', '@{upstream}').strip()
            if results == '':
                results = None
        except sh.ErrorReturnCode:
            pass

        self._remote_revision = results

    def _fetch(self):
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
            # error
            pass

    def _update_status(self, status=''):
        self._status = status

        enabled, enabled_status = self._check_enabled()

        if not enabled:
            self._status = enabled_status
        else:
            temp_status = []
            if self._commits_behind is not None:
                temp_status.append('{0} commit{1} behind'.format(self._commits_behind, 's' if self._commits_behind > 1 else ''))

            if self._commits_ahead is not None and self._commits_ahead > 0:
                temp_status.append('{0} commit{1} ahead'.format(self._commits_ahead, 's' if self._commits_ahead > 1 else ''))

            if len(temp_status) == 0:
                self._status = 'Up to date!'
            else:
                self._status += ', '.join(temp_status)

    def _check_enabled(self):
        git_available = self._git is not None
        remote_okay = self._check_remotes()

        status = ''
        if not git_available:
            status = 'Disabled (Git is unavailable)'

        if not remote_okay:
            status = 'Disabled (SSH origin)'

        return (git_available and remote_okay, status)

    def _check_remotes(self):
        """ Hack of a check determine if our origin remote is via ssh since it blocks if the key has a password. """
        ret = True

        remotes = self._git.remote(v=True)
        for r in remotes.strip().split("\n"):
            name, path = r.split("\t")
            if name == 'origin' and '@' in path:
                ret = False

        return ret


class DBUpdater(object):
    def __init__(self):
        self._config = Config()
        self._config.set_main_option("script_location", "alembic")

        self._script = ScriptDirectory.from_config(self._config)
        self._engine = create_engine(current_app.config.get('SQLALCHEMY_DATABASE_URI'))

    @property
    def needs_update(self):
        if self.current_revision != self.newest_revision:
            return True

        return False

    @property
    def current_revision(self):
        return self._current_revision

    @property
    def newest_revision(self):
        return self._newest_revision

    @property
    def status(self):
        return 'hi'

    def refresh(self):
        self._open()

        self._current_revision = self._context.get_current_revision()
        self._newest_revision = self._script.get_current_head()

        self._close()

    def update(self):
        if self._current_revision != self._newest_revision:
            try:
                command.upgrade(self._config, 'head')
            except sqlalchemy.exc.OperationalError, err:
                return False

        return True

    def _open(self):
        self._connection = self._engine.connect()
        self._context = MigrationContext.configure(self._connection)

    def _close(self):
        self._connection.close()
        self._connection = self._context = None
