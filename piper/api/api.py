from flask import Flask
from flask.ext.restful import Api
from flask.ext.restful.representations import json as rest_json

from piper.api import build
from piper.db.core import LazyDatabaseMixin

app = Flask(__name__)
api = Api(app)


class ApiCLI(LazyDatabaseMixin):
    def __init__(self, config):
        self.config = config

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('api', help='Control the REST API')

        sub = api.add_subparsers(help='API commands', dest="api_command")
        sub.add_parser('start', help='Start the API')

        return 'api', self.run

    def get_modules(self):  # pragma: nocover
        return (build,)

    def run(self, ns):
        # Patch the settings so that we get a proper JSON serializer for
        # whatever kind of objects we are going to return.
        rest_json.settings.update(self.db.json_settings)

        for mod in self.get_modules():
            for resource in mod.RESOURCES:
                # Give the configuration to the resource.
                # There might be a better way of doing this, but since we are
                # not doing the instantiation of the resource objects it's
                # difficult to actually pass arguments to it.
                resource.config = self.config
                api.add_resource(resource, '/api' + resource.root)

        app.run(debug=True)
