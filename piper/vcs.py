import logbook
import os

from git import Repo
from github import Github
from piper import utils


# TODO: Refactor to not use getters but properties
class VCS:
    def __init__(self, name, root_url, config):
        self.name = name
        self.root_url = root_url
        self.config = config

        self.log = logbook.Logger('{0}: {1}'.format(
            self.__class__.__name__, self.name
        ))

    def get_project(self, project):
        raise NotImplementedError()

    def get_project_name(self, build):
        raise NotImplementedError()


class GitVCS(VCS):
    """
    VCS class that knows how to git!

    """

    def get_project_name(self):
        name = utils.oneshot('git config remote.origin.url')
        return name.split(':')[1].replace('.git', '')


class GithubVCS(GitVCS):
    """
    Special class that handles Github specific things.

    """

    def __init__(self, name, root_url, config):
        super().__init__(name, root_url, config)

        # TODO: Non-anonymous access
        # TODO: Github Enterprise
        self.site = Github()

        # Repo representation on Github
        self.github = None

        # Repo representation on disk
        self.disk = None

        self.nwo = '{owner}/{name}'.format(**config['vcs'])

    def setup(self):
        """
        Perform setup steps.

        Connects to Github and gets the repo.

        """

        self.log.debug('Grabbing repository from {}...'.format(self.root_url))
        self.github = self.site.get_repo(self.nwo)
        self.log.debug('Got repo.')

    def clone(self, to_path=None):
        """
        Clone the repository to disk.

        Will set the `self.disk` attribute to be a `git.Repo` object.

        """

        if to_path is None:
            to_path = os.cwd()

        self.log.info('Cloning {} into {}...'.format(
            self.github.ssh_url,
            to_path
        ))

        self.disk = Repo.clone_from(self.github.ssh_url, to_path)

        self.log.info('Cloned.')
