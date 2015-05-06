import asyncio

from piper.api import ApiCLI

from mock import MagicMock
from mock import Mock
from mock import patch
import pytest

@pytest.fixture
def cli():
    cli = ApiCLI(Mock())
    cli.setup = Mock()
    cli._modules = [Mock(), Mock()]

    return cli

@pytest.fixture
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    request.addfinalizer(lambda: loop.close())

    return loop


class TestApiCLISetup:
    ...


class TestApiCLIRun:
    def test_calls(self, cli):
        cli.run()

        cli.setup().run_forever.assert_called_once_with()


class TestApiCliSetupLoop(object):
    @patch('aiohttp.web.Application')
    def test_application_creation(self, Application, cli, loop):
        loop.run_until_complete(cli.setup_loop(loop))

        Application.assert_called_once_with(loop=loop)

    @patch('aiohttp.web.Application')
    def test_module_setup(self, Application, cli, loop):
        loop.run_until_complete(cli.setup_loop(loop))

        app = Application()
        cli.modules[0].setup.assert_called_once_with(app)
        cli.modules[1].setup.assert_called_once_with(app)

    @patch('aiohttp.web.Application')
    def test_server_call(self, Application, cli, loop):
        loop.create_server = MagicMock()
        loop.create_server.return_value.iter.return_value = iter([1])

        loop.run_until_complete(cli.setup_loop(loop))

        app = Application()
        loop.create_server.assert_called_once_with(
            app.make_handler(),
            '127.0.0.1',
            8000,
        )
