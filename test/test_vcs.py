import pytest

from piper.vcs import VCSBase


class TestVCSBaseGetProject(object):
    def setup_method(self, method):
        self.vcs = VCSBase('name', 'root')
        self.project = 'bourne'

    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            self.vcs.get_project(self.project)
