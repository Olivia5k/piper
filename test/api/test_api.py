from piper.api.api import ApiCLI

import mock


class TestApiCLISetup(object):
    def setup_method(self, method):
        self.config = mock.Mock()

        self.cli = ApiCLI(self.config)
        self.cli.db = mock.Mock()
        self.cli.app = mock.Mock()
        self.cli.api = mock.Mock()
        self.cli.patch_json = mock.Mock()

        self.modules = (mock.Mock(),)
        self.cli.get_modules = mock.Mock()
        self.cli.get_modules.return_value = self.modules

        for mod in self.modules:
            mod.RESOURCES = (mock.Mock(root='/venus'),)

    def assert_config(self):
        for mod in self.modules:
            for resource in mod.RESOURCES:
                assert resource.config is self.config

    def test_calls(self):
        self.cli.setup()

        api_calls = [mock.call(self.modules[0].RESOURCES[0], '/api/venus')]
        self.cli.api.add_resource.assert_has_calls(api_calls)
        self.cli.patch_json.assert_called_once_with()

    def test_multiple_modules(self):
        self.modules = (mock.Mock(), mock.Mock(), mock.Mock())

        names = ('/greatest', '/songs', '/written')
        for root, mod in zip(names, self.modules):
            mod.RESOURCES = (mock.Mock(root=root),)

        self.cli.get_modules.return_value = self.modules

        self.cli.setup()

        api_calls = [
            mock.call(self.modules[0].RESOURCES[0], '/api/greatest'),
            mock.call(self.modules[1].RESOURCES[0], '/api/songs'),
            mock.call(self.modules[2].RESOURCES[0], '/api/written'),
        ]
        self.cli.api.add_resource.assert_has_calls(api_calls)
        self.assert_config()

    def test_multiple_resources(self):
        for mod in self.modules:
            mod.RESOURCES = (
                mock.Mock(root='/i'),
                mock.Mock(root='/need'),
                mock.Mock(root='/a'),
                mock.Mock(root='/lover'),
            )

        self.cli.setup()

        api_calls = [
            mock.call(self.modules[0].RESOURCES[0], '/api/i'),
            mock.call(self.modules[0].RESOURCES[1], '/api/need'),
            mock.call(self.modules[0].RESOURCES[2], '/api/a'),
            mock.call(self.modules[0].RESOURCES[3], '/api/lover'),
        ]
        self.cli.api.add_resource.assert_has_calls(api_calls)
        self.assert_config()


class TestApiCLIPatchJson(object):
    def setup_method(self, method):
        self.cli = ApiCLI(mock.Mock())
        self.cli.db = mock.Mock()

    @mock.patch('piper.api.api.rest_json')
    def test_patch(self, rj):
        self.cli.patch_json()
        rj.settings.update.assert_called_once_with(self.cli.db.json_settings)


class TestApiCLIRun(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.ns = mock.Mock()

        self.cli = ApiCLI(self.config)
        self.cli.setup = mock.Mock()
        self.cli.app = mock.Mock()

    def test_calls(self):
        self.cli.run(self.ns)
        self.cli.app.run.assert_called_once_with(debug=True)
