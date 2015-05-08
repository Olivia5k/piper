import asyncio

from piper.api import ApiCLI
from piper.config import AgentConfig

from mock import MagicMock
from mock import Mock
from mock import patch
import pytest


@pytest.fixture
def cli():
    config = AgentConfig()
    config.load()

    cli = ApiCLI(config)
    cli.setup = Mock()
    cli._modules = [Mock(), Mock()]

    return cli


@pytest.fixture
def event_loop_hehe(request):
    event_loop = asyncio.new_event_event_loop()
    asyncio.set_event_event_loop(None)

    request.addfinalizer(lambda: event_loop.close())

    return event_loop


class TestApiCLISetup:
    ...


class TestApiCLIRun:
    def test_calls(self, cli):
        cli.run()

        cli.setup().run_forever.assert_called_once_with()


class TestApiCliSetupEvent_Loop(object):
    @patch('aiohttp.web.Application')
    def test_application_creation(self, Application, cli, event_loop):
        event_loop.create_server = MagicMock()
        event_loop.run_until_complete(cli.setup_loop(event_loop))

        Application.assert_called_once_with(loop=event_loop)

    @patch('aiohttp.web.Application')
    def test_module_setup(self, Application, cli, event_loop):
        event_loop.create_server = MagicMock()
        event_loop.run_until_complete(cli.setup_loop(event_loop))

        app = Application()
        cli.modules[0].setup.assert_called_once_with(app)
        cli.modules[1].setup.assert_called_once_with(app)

    @patch('aiohttp.web.Application')
    def test_server_call(self, Application, cli, event_loop):
        event_loop.create_server = MagicMock()
        event_loop.create_server.return_value.iter.return_value = iter([1])

        event_loop.run_until_complete(cli.setup_loop(event_loop))

        app = Application()
        event_loop.create_server.assert_called_once_with(
            app.make_handler(),
            cli.config.raw['api']['address'],
            cli.config.raw['api']['port'],
        )
