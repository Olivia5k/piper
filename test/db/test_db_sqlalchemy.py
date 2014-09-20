import os

from piper.db.db_sqlalchemy import SQLAlchemyDB
from piper.db.db_sqlalchemy import in_session

from piper.db.db_sqlalchemy import VCSRoot
from piper.db.db_sqlalchemy import Agent
from piper.db.db_sqlalchemy import Project

import mock
import pytest


class SQLAlchemyDBBase(object):
    def setup_method(self, method):
        self.db = SQLAlchemyDB()
        self.ns = mock.Mock()
        self.config = mock.Mock()


class TestSQLAlchemyDBSetup(SQLAlchemyDBBase):
    @mock.patch('piper.db.db_sqlalchemy.create_engine')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_setup(self, se, ce):
        config = mock.Mock()
        self.db.setup(config)

        assert self.db.config is config
        ce.assert_called_once_with(config.db.host)
        se.configure.assert_called_once_with(bind=ce.return_value)


class TestSQLAlchemyDBInit(SQLAlchemyDBBase):
    def test_no_db(self):
        self.config.db.host = None

        with pytest.raises(AssertionError):
            self.db.init(self.ns, self.config)

    def test_calls(self):
        self.db.handle_sqlite = mock.Mock()
        self.db.create_tables = mock.Mock()

        self.db.init(self.ns, self.config)

        self.db.handle_sqlite.assert_called_once_with(self.config.db.host)
        self.db.create_tables.assert_called_once_with(
            self.config.db.host,
            echo=self.ns.verbose,
        )


class TestSQLAlchemyDBHandleSqlite(SQLAlchemyDBBase):
    @mock.patch('piper.utils.mkdir')
    @mock.patch('os.path.dirname')
    @mock.patch('os.path.exists')
    def test_sqlite_handling_creates_dir(self, exists, dirname, mkdir):
        self.config.db.host = 'sqlite:///amaranthine.db'
        exists.return_value = False

        self.db.handle_sqlite(self.ns.host)
        mkdir.assert_called_once_with(dirname.return_value)


class TestSQLAlchemyDBCreateTables(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBCreateTables, self).setup_method(method)
        self.db.tables = (mock.Mock(), mock.Mock())

        for x, table in enumerate(self.db.tables):
            table.__tablename__ = x

    @mock.patch('piper.db.db_sqlalchemy.Session')
    @mock.patch('piper.db.db_sqlalchemy.create_engine')
    def test_creation(self, ce, se):
        eng = ce.return_value
        host = self.config.host

        self.db.create_tables(host)

        ce.assert_called_once_with(host, echo=False)
        se.configure.assert_called_once_with(bind=eng)

        for table in self.db.tables:
            assert table.metadata.bind is eng
            table.metadata.create_all.assert_called_once_with()


class TestSQLAlchemyDBGetOrCreate(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBGetOrCreate, self).setup_method(method)
        self.session = mock.Mock()
        self.model = mock.Mock()
        self.kwargs = {'life is a grave': 'i dig it'}
        self.filter = self.session.query.return_value.filter_by

    def test_already_exists(self):
        ret = self.db.get_or_create(self.session, self.model, **self.kwargs)

        assert ret is self.filter.return_value.first.return_value
        assert self.session.add.call_count == 0

    def test_does_not_exist(self):
        self.filter.return_value.first.return_value = None

        self.db.get_or_create(self.session, self.model, **self.kwargs)

        self.model.assert_called_once_with(**self.kwargs)
        self.session.add.assert_called_once_with(self.model.return_value)


class TestSQLAlchemyDBAddBuild(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBAddBuild, self).setup_method(method)
        self.build = mock.Mock()
        self.build.default_db_kwargs.return_value = {'cave': 'canem'}
        self.db.get_agent = mock.Mock()
        self.db.get_project = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_id_is_returned(self, sess, table):
        ret = self.db.add_build(self.build)

        assert ret is table.return_value.id

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_instance_added_to_session(self, sess, table):
        self.db.add_build(self.build)

        sess.return_value.add.assert_called_once_with(table.return_value)


class TestSQLAlchemyDBUpdateBuild(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBUpdateBuild, self).setup_method(method)
        self.build = mock.MagicMock()
        self.extra = {'island in the sun': 'only way for things to come'}

    @mock.patch('piper.db.db_sqlalchemy.update')
    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_values(self, session, table, update):
        self.db.update_build(self.build, **self.extra)

        self.build.default_db_kwargs.assert_called_once_with()
        values = self.build.default_db_kwargs.return_value
        values.update.assert_called_once_with(self.extra)

    @mock.patch('piper.db.db_sqlalchemy.update')
    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_database_chain(self, session, table, update):
        # Fake the comparison thingy that SQLAlchemy uses to make constructor
        # objects. Default for the mock seems to be actually not mocked, even
        # when it's magic.
        table.id.__eq__ = mock.Mock()

        self.db.update_build(self.build, **self.extra)

        args = self.build.default_db_kwargs.return_value
        where = update.return_value.where
        values = where.return_value.values

        update.assert_called_once_with(table)
        where.assert_called_once_with(table.id.__eq__.return_value)
        values.assert_called_once_with(args)

    @mock.patch('piper.db.db_sqlalchemy.update')
    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_execution(self, session, table, update):
        self.db.update_build(self.build, **self.extra)

        stmt = update.return_value.where.return_value.values.return_value
        session.return_value.execute.assert_called_once_with(stmt)


class TestSQLAlchemyDBGetProject(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBGetProject, self).setup_method(method)
        self.build = mock.Mock()
        self.db.get_vcs = mock.Mock()
        self.db.get_or_create = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value_is_project(self, session):
        ret = self.db.get_project(self.build)
        assert ret is self.db.get_or_create.return_value

    @mock.patch('piper.db.db_sqlalchemy.Project')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments(self, session, table):
        self.db.get_project(self.build)

        self.db.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            name=self.build.vcs.get_project_name.return_value,
            vcs=self.db.get_vcs.return_value
        )


class TestSQLAlchemyDBGetVcs(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBGetVcs, self).setup_method(method)
        self.build = mock.Mock()
        self.db.get_or_create = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value_is_vcs(self, session):
        ret = self.db.get_vcs(self.build)
        assert ret is self.db.get_or_create.return_value

    @mock.patch('piper.db.db_sqlalchemy.VCSRoot')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments(self, session, table):
        self.db.get_vcs(self.build)

        self.db.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            expunge=False,
            root_url=self.build.vcs.root_url,
            name=self.build.vcs.name,
        )

    @mock.patch('piper.db.db_sqlalchemy.VCSRoot')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments_with_expunge(self, session, table):
        self.db.get_vcs(self.build, expunge=True)

        self.db.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            expunge=True,
            root_url=self.build.vcs.root_url,
            name=self.build.vcs.name,
        )


class TestSQLAlchemyDBGetAgent(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBGetAgent, self).setup_method(method)
        self.db.get_or_create = mock.Mock()

    @mock.patch('socket.gethostname')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value_is_agent(self, session, gh):
        ret = self.db.get_agent()
        assert ret is self.db.get_or_create.return_value

    @mock.patch('socket.gethostname')
    @mock.patch('piper.db.db_sqlalchemy.Agent')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments(self, session, table, gh):
        self.db.get_agent()

        self.db.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            name=gh.return_value,
            fqdn=gh.return_value,
            active=True,
            busy=False,
            registered=False,
        )


class TestInSessionInner(object):
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_context_is_a_session(self, session):
        with in_session() as val:
            assert val is session.return_value

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_exception_rolls_back(self, session):
        with pytest.raises(ValueError):
            with in_session():
                raise ValueError('zomg')

        session.return_value.rollback.assert_called_once_with()
        session.return_value.close.assert_called_once_with()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_automatic_commit(self, session):
        with in_session():
            pass

        session.return_value.commit.assert_called_once_with()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_automatic_close(self, session):
        with in_session():
            pass

        session.return_value.close.assert_called_once_with()


class TestSQLiteIntegration(SQLAlchemyDBBase):
    """
    These are tests that actually create objects in the database and retrieve
    them to check the validity.

    """

    def setup_method(self, method):
        super(TestSQLiteIntegration, self).setup_method(method)

        self.config.db.host = 'sqlite:///test.db'
        self.config.db.singleton = True
        self.ns.verbose = False

        self.db.init(self.ns, self.config)
        self.db.setup(self.config)

        self.build = mock.Mock()

    def teardown_method(self, method):
        os.remove('test.db')

    def test_get_vcs(self):
        self.build.vcs.name = 'oh sailor'
        self.build.vcs.root_url = 'fiona://extraordinary-machine.net'

        self.db.get_vcs(self.build)

        with in_session() as session:
            assert session.query(VCSRoot).count() == 1

            vcs = session.query(VCSRoot).first()
            assert vcs.name == self.build.vcs.name
            assert vcs.root_url == self.build.vcs.root_url

    @mock.patch('socket.gethostname')
    def test_get_agent(self, gh):
        hostname = 'shadow.cabinet'
        gh.return_value = hostname
        self.db.get_agent()

        with in_session() as session:
            assert session.query(Agent).count() == 1

            agent = session.query(Agent).first()
            assert agent.name == hostname
            assert agent.fqdn == hostname
            assert agent.active is True
            assert agent.busy is False
            assert agent.registered is False

    def test_get_project(self):
        self.build.vcs.name = 'apathy divine'
        self.build.vcs.root_url = 'tokenring://wutheringheights.dk'
        self.build.vcs.get_project_name.return_value = 'mandatory/fun'

        self.db.get_project(self.build)

        with in_session() as session:
            assert session.query(Project).count() == 1
            assert session.query(VCSRoot).count() == 1

            vcs = session.query(VCSRoot).first()
            assert vcs.name == self.build.vcs.name
            assert vcs.root_url == self.build.vcs.root_url

            project = session.query(Project).first()
            assert project.name == 'mandatory/fun'
