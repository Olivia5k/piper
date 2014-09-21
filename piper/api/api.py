from flask import Flask
from flask.ext.restful import Api
from flask.ext.restful.representations import json as rest_json

from piper.api import build
from piper.db.core import LazyDatabaseMixin


class ApiCLI(LazyDatabaseMixin):
    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__)
        self.api = Api(self.app)

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('api', help='Control the REST API')

        sub = api.add_subparsers(help='API commands', dest="api_command")
        sub.add_parser('start', help='Start the API')

        return 'api', self.run

    def get_modules(self):  # pragma: nocover
        return (build,)

    def patch_json(self):  # pragma: nocover
        # Patch the settings so that we get a proper JSON serializer for
        # whatever kind of objects we are going to return.
        rest_json.settings.update(self.db.json_settings)

    def run(self, ns):
        for mod in self.get_modules():
            for resource in mod.RESOURCES:
                # Give the configuration to the resource.
                # There might be a better way of doing this, but since we are
                # not doing the instantiation of the resource objects it's
                # difficult to actually pass arguments to it.
                resource.config = self.config
                self.api.add_resource(resource, '/api' + resource.root)

        self.patch_json()
        self.app.run(debug=True)
