import sh
from sh import git

class Updater(object):
    def __init__(self):
        self._components = {}

        self._components['webapp'] = SourceUpdater('webapp')

    def check_updates(self):
        needs_update = {}

        for name, component in self._components.iteritems():
            if component.needs_update():
                behind, ahead = component.commit_count()
                status = self._format_status(behind, ahead)

                needs_update[name] = (component.branch(), component.local_revision(), component.remote_revision(), status)

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

    def _format_status(self, behind, ahead):
        status = ''

        if behind is not None or ahead is not None:
            status = '{0} commit{1} behind'.format(behind, 's' if behind > 1 else '')

            if ahead is not None:
                status += ' and '

        if ahead is not None and ahead > 0:
            status += '{0} commit{1} ahead'.format(ahead, 's' if ahead > 1 else '')

        if status == '': status = 'Up to date.'

        return status

class SourceUpdater(object):
    def __init__(self, name):
        self.name = name

    def needs_update(self):
        ahead, behind = self.commit_count()

        if behind is not None and behind > 0:
            return True

        return False

    def commit_count(self):
        ret = (None, None)
        try:
            results = git('rev-list', '@{upstream}...HEAD', left_right=True).strip()

            ret = (results.count('<'), results.count('>'))
        except sh.ErrorReturnCode:
            pass

        return ret

    def update(self, branch=None):
        return { 'status': 'PASS', 'restart_required': True }

    def branch(self):
        results = None
        try:
            results = git('symbolic-ref', 'HEAD', q=True).strip()
            results = results.replace('refs/heads/', '')
        except sh.ErrorReturnCode:
            pass

        return results

    def local_revision(self):
        results = None
        try:
            results = git('rev-parse', 'HEAD').strip()
        except sh.ErrorReturnCode:
            pass

        return results

    def remote_revision(self, branch=None):
        results = None
        try:
            results = git('rev-parse', '--verify', '--quiet', '@{upstream}').strip()
            if results == '':
                results = None
        except sh.ErrorReturnCode:
            pass

        return results


class DBUpdater(object):
    pass