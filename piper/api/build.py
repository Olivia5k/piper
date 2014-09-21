from flask.ext.restful import Resource

from piper.db.core import LazyDatabaseMixin


class Build(Resource, LazyDatabaseMixin):
    root = '/build/<int:build_id>'

    def get(self, build_id):
        """
        Get one build

        """

        build = self.db.get_build(build_id)

        if build is None:
            return {}, 404

        return build

    def delete(self, build_id):  # pragma: nocover
        """
        Cancel a build

        """

        raise NotImplementedError()
        self.db.cancel_build(build_id)
        return '', 204


class BuildList(Resource, LazyDatabaseMixin):
    root = '/build'

    def get(self):
        """
        Get a list of builds

        """

        # Pagination is for cowards and people that don't fight with swords.
        builds = self.db.get_builds()
        return builds

RESOURCES = (Build, BuildList)
