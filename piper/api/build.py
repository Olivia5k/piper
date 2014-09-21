from flask.ext.restful import Resource

from piper.db.core import LazyDatabaseMixin


class Build(Resource, LazyDatabaseMixin):
    endpoint = '/build/<int:build_id>'

    def get(self, build_id):
        """
        Get one build

        """

        build = self.db.get_build(build_id)

        if build is None:
            return {}, 404

        return build

    def delete(self, build_id):
        """
        Cancel a build

        """

        raise NotImplementedError()
        self.db.cancel_build(build_id)
        return '', 204


class BuildList(Resource, LazyDatabaseMixin):
    endpoint = '/build'

    def get(self):
        """
        Get a list of builds

        """

        raise NotImplementedError()


RESOURCES = (Build, BuildList)
