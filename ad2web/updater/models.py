import git

class Updater(object):
    def __init__(self):
        self._source_updater = SourceUpdater()

    def check_updates(self):
        needing_update = {}
        if self._source_updater.needs_update():
            behind, ahead = self._source_updater.commit_count()
            commit_string = '{0} commit{1} behind'.format(behind, 's' if behind > 1 else '')
            if ahead > 0:
                commit_string += ' and {0} commit{1} behind'.format(ahead, 's' if ahead > 1 else '')

            needing_update['webapp'] = (self._source_updater.branch(), self._source_updater.local_revision(), self._source_updater.remote_revision(), commit_string)

        return needing_update

    def update(self):
        if self._source_updater.needs_update():
            self._source_updater.update()

class SourceUpdater(object):
    def __init__(self, path='.'):
        try:
            self._repo = git.Repo(path)
        except git.exc.InvalidGitRepositoryError, err:
            self._repo = None

    def needs_update(self):
        if self._repo is None:
            return False

        local_revision = self.local_revision()
        remote_revision = self.remote_revision()

        if remote_revision is not None and local_revision != remote_revision:
            return True

        return False

    def commit_count(self):
        remote = 'origin'
        branch = self.branch()
        results = self._repo.git.rev_list('{remote}...{local}'.format(remote=self._repo.remotes[remote].refs[branch], local=branch), left_right=True)

        return (results.count('<'), results.count('>'))

    def update(self, branch=None):
        if branch is None:
            branch = self.branch()

        self._repo.remotes.origin.pull(branch)

    def branch(self):
        try:
            branch_name = self._repo.active_branch.name
        except TypeError:
            return None

        return branch_name

    def local_revision(self):
        return str(self._repo.head.commit)

    def remote_revision(self, branch=None):
        if branch is None:
            branch = self.branch()

        self._repo.remotes.origin.fetch()

        remote_revision = None
        for ref in self._repo.remotes.origin.refs:
            if ref.remote_head == branch:
                remote_revision = str(ref.commit)

        return remote_revision

class DBUpdater(object):
    pass