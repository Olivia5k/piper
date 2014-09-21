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
        rest_json.settings.update(self.db.json_settings)

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('api', help='Control the REST API')

        sub = api.add_subparsers(help='API commands', dest="api_command")
        sub.add_parser('start', help='Start the API')

        return 'api', self.run

    def run(self, ns):
        for mod in (build,):
            for resource in mod.RESOURCES:
                # Give the configuration to the resource.
                # There might be a better way of doing this, but since we are
                # not doing the instanciation of the resource objects it's
                # difficult to actually pass arguments to it.
                resource.config = self.config
                api.add_resource(resource, '/api' + resource.endpoint)

        app.run(debug=True)
