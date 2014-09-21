from piper.api.api import ApiCLI

import mock


class TestApiCLIRun(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.ns = mock.Mock()

        self.cli = ApiCLI(self.config)
        self.cli.db = mock.Mock()

        self.modules = (mock.Mock(),)
        self.cli.get_modules = mock.Mock()
        self.cli.get_modules.return_value = self.modules

        for mod in self.modules:
            mod.RESOURCES = (mock.Mock(root='/venus'),)

    @mock.patch('piper.api.api.rest_json')
    @mock.patch('piper.api.api.app')
    @mock.patch('piper.api.api.api')  # hehe
    def test_calls(self, api, app, rest_json):
        self.cli.run(self.ns)

        rest_json.settings.update.assert_called_once_with(
            self.cli.db.json_settings
        )

        api_calls = [mock.call(self.modules[0].RESOURCES[0], '/api/venus')]
        api.add_resource.assert_has_calls(api_calls)
        app.run.assert_called_once_with(debug=True)

    @mock.patch('piper.api.api.rest_json')
    @mock.patch('piper.api.api.app')
    @mock.patch('piper.api.api.api')
    def test_multiple_modules(self, api, app, rest_json):
        self.modules = (mock.Mock(), mock.Mock(), mock.Mock())

        names = ('/greatest', '/songs', '/written')
        for root, mod in zip(names, self.modules):
            mod.RESOURCES = (mock.Mock(root=root),)

        self.cli.get_modules.return_value = self.modules

        self.cli.run(self.ns)

        api_calls = [
            mock.call(self.modules[0].RESOURCES[0], '/api/greatest'),
            mock.call(self.modules[1].RESOURCES[0], '/api/songs'),
            mock.call(self.modules[2].RESOURCES[0], '/api/written'),
        ]
        api.add_resource.assert_has_calls(api_calls)

    @mock.patch('piper.api.api.rest_json')
    @mock.patch('piper.api.api.app')
    @mock.patch('piper.api.api.api')
    def test_multiple_resources(self, api, app, rest_json):
        for mod in self.modules:
            mod.RESOURCES = (
                mock.Mock(root='/i'),
                mock.Mock(root='/need'),
                mock.Mock(root='/a'),
                mock.Mock(root='/lover'),
            )

        self.cli.run(self.ns)

        api_calls = [
            mock.call(self.modules[0].RESOURCES[0], '/api/i'),
            mock.call(self.modules[0].RESOURCES[1], '/api/need'),
            mock.call(self.modules[0].RESOURCES[2], '/api/a'),
            mock.call(self.modules[0].RESOURCES[3], '/api/lover'),
        ]
        api.add_resource.assert_has_calls(api_calls)
