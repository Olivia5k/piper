from piper.version import Version
from piper.version import StaticVersion
from piper.version import GitVersion

import jsonschema
import pytest
import mock


class StaticVersionBase(object):
    def setup_method(self, method):
        self.v = '32.1.12'
        self.version = StaticVersion(mock.Mock(), {
            'class': 'hehe',
            'version': self.v,
        })


class GitVersionBase(object):
    def setup_method(self, method):
        self.git = GitVersion(mock.Mock(), {
            'class': 'piper.version.GitVersion',
        })


class TestVersionValidate(object):
    @mock.patch('jsonschema.validate')
    def test_validate(self, jv):
        version = Version(mock.Mock(), {'version': 'hehe'})
        version.validate()

        jv.assert_called_once_with(
            version.config.data,
            version.schema
        )

    def test_broken_schema(self):
        version = Version(mock.Mock(), {'the_final_countdown': True})
        with pytest.raises(jsonschema.exceptions.ValidationError):
            version.validate()


class TestVersionGetVersion(object):
    def test_not_implemented(self):
        version = Version(mock.Mock(), {'the_final_countdown': True})
        with pytest.raises(NotImplementedError):
            version.get_version()


class TestStaticVersionGetVersion(StaticVersionBase):
    def test_get_version(self):
        ret = self.version.get_version()
        assert ret == self.v


class TestStaticVersionSchema(StaticVersionBase):
    def test_validation(self):
        self.version.validate()

    def test_validation_extra_field(self):
        self.version = StaticVersion(mock.Mock(), {
            'class': 'hehe',
            'version': '3',
            'stranger': 'in.you',
        })

        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.version.validate()


class TestGitVersionSchema(GitVersionBase):
    def test_validation(self):
        self.git.validate()

    def test_validation_extra_field(self):
        self.git.config.data['tyger'] = True
        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.git.validate()


class TestGitVersionGetVersion(GitVersionBase):
    @mock.patch('piper.version.oneshot')
    def test_get_version(self, os):
        self.git.get_version()
        os.assert_called_once_with('git describe --tags')

    @mock.patch('piper.version.oneshot')
    def test_get_version_with_arguments(self, os):
        flags = '--apathy-divine --snow'
        self.git.config.arguments = flags
        self.git.get_version()
        os.assert_called_once_with('git describe {0}'.format(flags))
