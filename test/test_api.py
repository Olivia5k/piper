from piper.api import ApiCLI
from piper.api import RESTful
from piper.api import date_handler
from piper.config import AgentConfig

from mock import MagicMock
from mock import Mock
from mock import patch
from mock import call
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
def restful():
    config = AgentConfig()
    config.load()
    rest = RESTful(config)
    rest.routes = [
        ('PLS', '/no', Mock()),
        ('HAX', '/lel', Mock()),
    ]
    return rest


def wrap(func):
    rest = restful()
    enc = Mock()
    rest.encode_response = enc
    with patch('asyncio.coroutine') as cr:
        func = rest.endpoint(func)
        return (cr.call_args_list[0][0][0], enc)


@pytest.fixture
def app():
    return Mock()


class TestApiCLIRun:
    def test_calls(self, cli):
        cli.run()

        cli.setup().run_forever.assert_called_once_with()


class TestApiCliSetupLoop(object):
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


class TestRestfulSetup(object):
    def test_route_calls(self, restful, app):
        restful.endpoint = Mock()
        restful.setup(app)

        ar = app.router.add_route
        assert ar.call_count == 2

        ar.assert_has_calls([
            call('PLS', '/no', restful.endpoint.return_value),
            call('HAX', '/lel', restful.endpoint.return_value),
        ])


class TestRestfulEndpoint(object):
    """
    Tests the decorator method that takes care of wrapping requests not only
    in a response handler and JSON encoder but also in a asyncio.Web handler.

    The slight complexity and repetition of these tests are a tradeoff for
    making the decorator as easy as possible to use. One rationalisation is
    that we will write a lot more endpoints than we will write endpoint
    definitions.

    """

    @patch('asyncio.coroutine')
    def test_result_is_a_coroutine(self, coroutine, restful):
        func = Mock()
        ret = restful.endpoint(func)
        assert ret is coroutine()

    def test_wrap_result_with_code(self, restful):
        func = Mock(return_value=("stanton.creed", 3001))

        inner, enc = wrap(func)
        ret = inner()
        assert ret is enc.return_value
        enc.assert_called_once_with("stanton.creed", 3001)

    def test_wrap_result_without_code(self, restful):
        func = Mock(return_value=("six.to.midnight"))

        inner, enc = wrap(func)
        ret = inner()
        assert ret is enc.return_value
        enc.assert_called_once_with("six.to.midnight", 200)


class TestRestfulEncodeResponse(object):
    @patch('json.dumps')
    @patch('aiohttp.web.Response')
    def test_encoding(self, response, dumps, restful):
        body = {'autumn': 'fight like a girl'}
        code = 2012
        ret = restful.encode_response(body, code)

        assert ret is response.return_value
        dumps.assert_called_once_with(
            body,
            indent=2,
            sort_keys=True,
            default=date_handler,
        )
        response.assert_called_once_with(
            body=dumps.return_value.encode.return_value,
            status=code,
            headers={'content-type': 'application/json'},
        )
