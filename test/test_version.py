from piper.version import Version
from piper.version import StaticVersion

import jsonschema
import pytest
import mock


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


class TestStaticVersionGetVersion(object):
    def test_get_version(self):
        v = '32.1.12'
        version = StaticVersion(mock.Mock(), {'version': v})

        ret = version.get_version()
        assert ret == v
