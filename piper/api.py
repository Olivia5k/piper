import asyncio
import json
import logbook

from aiohttp import web
from piper.db.core import LazyDatabaseMixin


class ApiCLI(LazyDatabaseMixin):
    _modules = None

    def __init__(self, config):
        self.config = config

        self.log = logbook.Logger(self.__class__.__name__)

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('api', help='Control the REST API')

        sub = api.add_subparsers(help='API commands', dest="api_command")
        sub.add_parser('start', help='Start the API')

        return 'api', self.run

    @property
    def modules(self):  # pragma: nocover
        """
        Get a tuple of the modules that should be in the API.

        This should probably be programmatically built rather than statically.

        """

        if self._modules is not None:
            return self._modules

        from piper.build import BuildAPI

        return (
            BuildAPI(self.config),
        )

    @asyncio.coroutine
    def setup_loop(self, loop):
        app = web.Application(loop=loop)

        for mod in self.modules:
            mod.setup(app)

        srv = yield from loop.create_server(
            app.make_handler(),
            self.config.raw['api']['address'],
            self.config.raw['api']['port'],
        )

        self.log.info(
            "Server started at http://{address}:{port}".format(
                **self.config.raw['api']
            )
        )
        return srv

    def setup(self):  # pragma: nocover
        loop = asyncio.get_event_loop()
        setup_future = self.setup_loop(loop)
        loop.run_until_complete(setup_future)
        return loop

    def run(self):
        loop = self.setup()
        loop.run_forever()


class RESTful(LazyDatabaseMixin):
    """
    Abstract class pertaining to a RESTful API endpoint for aiohttp.

    Anything that inherits for this has to set `self.routes` to be a tuple like
    .. code-block::
       routes = (
          ("POST", "/foo", self.post),
          ("GET", "/foo", self.get),
       )

    When :func:`setup` is ran, the routes will be added to the aiohttp app.
    See :class:`piper.build.BuildAPI` for an example implementation.

    """

    def __init__(self, config):
        self.config = config

        self.log = logbook.Logger(self.__class__.__name__)

    def setup(self, app):
        """
        Register the routes to the application.

        Will decorate all methods with :func:`endpoint`

        """

        for method, route, function in self.routes:
            app.router.add_route(
                method,
                route,
                self.endpoint(function),
            )

    def endpoint(self, func):
        """
        Decorator method that takes care of calling and post processing
        responses.

        """

        def wrap(*args, **kwargs):
            body = func(*args, **kwargs)
            code = 200

            # TODO: Add JSONschema validation
            if isinstance(body, tuple):
                # If the result was a 2-tuple, use the second item as the
                # status code.
                body, code = body

            return self.encode_response(body, code)

        return asyncio.coroutine(wrap)

    def encode_response(self, body, code):
        body = json.dumps(
            body,
            indent=2,
            sort_keys=True,
            default=date_handler,
        )

        response = web.Response(
            body=body.encode(),
            status=code,
            headers={'content-type': 'application/json'}
        )

        return response


def date_handler(obj):  # pragma: nocover
    """
    This is why we cannot have nice things.
    https://stackoverflow.com/questions/455580/

    """

    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, ...):
        return ...
    else:
        raise TypeError(
            'Object of type %s with value of %s is not JSON serializable' % (
                type(obj), repr(obj)
            )
        )
