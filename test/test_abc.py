from piper.abc import DynamicItem

import mock
import pytest


class TestDynamicItemValidateRequirements:
    def setup_method(self, method):
        self.build = mock.Mock()

        self.cls = mock.Mock()

        self.first_key = 'one.day'
        self.first = {
            'reason': '...and our children would play.',
            'key': 'virtual',
            'equals': 'physical',
        }

        self.second_key = 'live.again'
        self.second = {
            'reason': 'Desperate, tenacious, clinging like a grain of sand',
            'key': 'live',
            'equals': 'again',
        }

    def test_no_requirements(self):
        self.item = DynamicItem(self.build, {})
        self.item.validate_requirements()

    @pytest.mark.skipif(True, reason="refactor skip")
    def test_requirement_calls(self):
        """
        Validates that given the schema, the method `equals` should have been
        called on an instance of the class `self.cls` with the argument
        `'physical'`

        """

        self.cls = mock.Mock()
        self.cls_key = 'piper.prop.FacterProp'

        self.item = DynamicItem(self.build, {
            'requirements': {
                self.first_key: self.first
            },
        })

        self.item.build = mock.Mock()
        self.item.build.config.classes = {}
        self.item.build.config.classes[self.cls_key] = self.cls

        self.item.validate_requirements()

        self.cls.assert_called_once_with(self.first['key'])
        self.cls.return_value.validate.assert_called_once_with(self.first)

    @pytest.mark.skipif(True, reason="refactor skip")
    def test_multiple_requirement_calls(self):
        self.item = DynamicItem(self.build, {
            'requirements': {
                self.first_key: self.first,
                self.second_key: self.second,
            }
        })

        self.item.build = mock.Mock()
        self.item.build.config.classes = {}
        self.item.build.config.classes[self.cls_key] = self.cls

        self.item.validate_requirements()

        calls = [mock.call(self.first), mock.call(self.second)]
        self.cls.return_value.validate.assert_has_calls(calls, any_order=True)
