import sh
from sh import git
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
        needs_update = {}

        for name, component in self._components.iteritems():
            component.refresh()
            if component.needs_update:
                needs_update[name] = (component.branch, component.local_revision, component.remote_revision, component.status)

        return needs_update

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
        self.name = name
        self._branch = 'master'
        self._local_revision = None
        self._remote_revision = None
        self._commits_ahead = 0
        self._commits_behind = 0

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
        behind, ahead = self.commit_count

        if behind is not None and behind > 0:
            return True

        return False

    def refresh(self):
        self._fetch()

        self._retrieve_branch()
        self._retrieve_local_revision()
        self._retrieve_remote_revision()
        self._retrieve_commit_count()

        self._db_updater.refresh()

    def update(self, branch=None):
        try:
            #results = git.merge('origin/{0}'.format(self.branch()))

            self._db_updater.update()
        except sh.ErrorReturnCode, err:
            # error
            pass

        return { 'status': 'PASS', 'restart_required': True }

    def _retrieve_commit_count(self):
        try:
            results = git('rev-list', '@{upstream}...HEAD', left_right=True).strip()

            self._commits_behind, self._commits_ahead = results.count('<'), results.count('>')
            self._update_status()
        except sh.ErrorReturnCode:
            pass

    def _retrieve_branch(self):
        try:
            results = git('symbolic-ref', 'HEAD', q=True).strip()
            self._branch = results.replace('refs/heads/', '')
        except sh.ErrorReturnCode:
            pass

    def _retrieve_local_revision(self):
        try:
            results = git('rev-parse', 'HEAD')

            self._local_revision = results.strip()
        except sh.ErrorReturnCode:
            pass

    def _retrieve_remote_revision(self):
        results = None

        try:
            results = git('rev-parse', '--verify', '--quiet', '@{upstream}').strip()
            if results == '':
                results = None
        except sh.ErrorReturnCode:
            pass

        self._remote_revision = results

    def _fetch(self):
        try:
            results = git.fetch('origin')
        except sh.ErrorReturnCode:
            # error
            pass

    def _update_status(self):
        status = []

        if self._commits_behind is not None:
            status.append('{0} commit{1} behind'.format(self._commits_behind, 's' if self._commits_behind > 1 else ''))

        if self._commits_ahead is not None and self._commits_ahead > 0:
            status.append('{0} commit{1} ahead'.format(self._commits_ahead, 's' if self._commits_ahead > 1 else ''))

        self._status = ', '.join(status)


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
            print '------------------------- Updating now..', self._current_revision, self._newest_revision
            try:
                command.upgrade(self._config, 'head')
            except sqlalchemy.exc.OperationalError, err:
                print '--------------------------- Error while updating..', err
            else:
                print '--------------------------- Finished updating!'
        else:
            print '------------------------------ Up to date!'

    def _open(self):
        self._connection = self._engine.connect()
        self._context = MigrationContext.configure(self._connection)

    def _close(self):
        self._connection.close()
        self._connection = self._context = None
