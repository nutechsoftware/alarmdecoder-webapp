import sh
from sh import git

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

    def update(self, branch=None):
        try:
            #results = git.merge('origin/{0}'.format(self.branch()))
            pass
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
    pass