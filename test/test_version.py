from piper.version import Version
from piper.version import StaticVersion
from piper.version import GitVersion

import jsonschema
import pytest
import mock


class StaticVersionTest:
    def setup_method(self, method):
        self.build = mock.Mock()
        self.v = '32.1.12'
        self.raw = {
            'class': 'hehe',
            'version': self.v,
        }
        self.version = StaticVersion(self.build, self.raw)


class GitVersionTest:
    def setup_method(self, method):
        self.build = mock.Mock()
        self.raw = {
            'class': 'piper.version.GitVersion',
        }
        self.git = GitVersion(self.build, self.raw)


class TestVersionValidate:
    def test_broken_schema(self):
        version = Version(mock.Mock(), mock.Mock(the_final_countdown=True))
        with pytest.raises(jsonschema.exceptions.ValidationError):
            version.validate()


class TestVersionGetVersion:
    def test_not_implemented(self):
        version = Version(mock.Mock(), mock.Mock())
        with pytest.raises(NotImplementedError):
            version.get_version()


class TestStaticVersionGetVersion(StaticVersionTest):
    def test_get_version(self):
        ret = self.version.get_version()
        assert ret == self.v


class TestGitVersionGetVersion(GitVersionTest):
    @mock.patch('piper.version.oneshot')
    def test_get_version(self, os):
        flags = '--tags'
        self.git.config['arguments'] = flags
        self.git.get_version()
        os.assert_called_once_with('git describe --tags')

    @mock.patch('piper.version.oneshot')
    def test_get_version_with_arguments(self, os):
        flags = '--apathy-divine --snow'
        self.git.config['arguments'] = flags
        self.git.get_version()
        os.assert_called_once_with('git describe {0}'.format(flags))
