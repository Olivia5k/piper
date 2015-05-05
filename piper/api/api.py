from flask import Flask
from flask.ext.restful import Api

from piper.api import build
from piper.db.core import LazyDatabaseMixin


class ApiCLI(LazyDatabaseMixin):
    def __init__(self, config):
        self.config = config
        self.app = Flask('piper')
        self.api = Api(self.app)

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('api', help='Control the REST API')

        sub = api.add_subparsers(help='API commands', dest="api_command")
        sub.add_parser('start', help='Start the API')

        return 'api', self.run

    def get_modules(self):  # pragma: nocover
        return (build,)

    def setup(self):
        for mod in self.get_modules():
            for resource in mod.RESOURCES:
                # Give the configuration to the resource.
                # There might be a better way of doing this, but since we are
                # not doing the instantiation of the resource objects it's
                # difficult to actually pass arguments to it.
                resource.config = self.config
                self.api.add_resource(resource, '/api' + resource.root)

    def run(self):
        self.setup()
        self.app.run(debug=True)
