import pytest
import mock

from piper.vcs import VCSBase
from piper.vcs import GitVCS


class VCSBaseTestBase(object):
    def setup_method(self, method):
        self.vcs = VCSBase('name', 'root')
        self.project = 'bourne'
        self.build = mock.Mock()

    def missing(self, name, *args, **kwargs):
        with pytest.raises(NotImplementedError):
            getattr(self.vcs, name)(*args, **kwargs)


class TestVCSBaseGetProject(VCSBaseTestBase):
    def test_raises_not_implemented_error(self):
            self.missing('get_project', self.project)


class TestVCSBaseGetProjectName(VCSBaseTestBase):
    def test_raises_not_implemented_error(self):
        self.missing('get_project_name', self.project)


class TestGitVCSGetProjectName(object):
    def setup_method(self, method):
        self.git = GitVCS('horny', 'hearse')

    @mock.patch('piper.utils.oneshot')
    def test_return_value(self, os):
        ret = self.git.get_project_name()
        split = os.return_value.split.return_value
        assert ret is split[1].replace.return_value

    @mock.patch('piper.utils.oneshot')
    def test_calls(self, os):
        self.git.get_project_name()
        os.assert_called_once_with('git config remote.origin.url')
        os.return_value.split.assert_called_once_with(':')
