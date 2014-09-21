import os
import datetime

from piper.db.db_sqlalchemy import SQLAlchemyDB
from piper.db.db_sqlalchemy import in_session

from piper.db.db_sqlalchemy import Agent
from piper.db.db_sqlalchemy import Build
from piper.db.db_sqlalchemy import Project
from piper.db.db_sqlalchemy import VCSRoot

import mock
import pytest


class SQLAlchemyDBBase(object):
    def setup_method(self, method):
        self.db = SQLAlchemyDB()
        self.ns = mock.Mock()
        self.config = mock.Mock()
        self.build = mock.Mock()


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
        self.kwargs = {
            'life is a grave': 'i dig it',
            'stanton': 'creed',
        }
        self.keys = ['stanton']
        self.filtered_keys = {'stanton': 'creed'}
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

    def test_filter_kwargs_without_keys(self):
        self.db.get_or_create(self.session, self.model, **self.kwargs)
        self.filter.assert_called_once_with(**self.kwargs)

    def test_filter_kwargs_with_keys(self):
        self.db.get_or_create(
            self.session, self.model, keys=self.keys, **self.kwargs
        )
        self.filter.assert_called_once_with(**self.filtered_keys)


class TestSQLAlchemyDBAddBuild(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBAddBuild, self).setup_method(method)
        self.build.default_db_kwargs.return_value = {'cave': 'canem'}
        self.db.get_agent = mock.Mock()
        self.db.get_project = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_object_ref_is_returned(self, sess, table):
        ret = self.db.add_build(self.build)

        assert ret is table.return_value

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_instance_added_to_session(self, sess, table):
        self.db.add_build(self.build)

        sess.return_value.add.assert_called_once_with(table.return_value)

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_instance_refreshed_and_expunged(self, sess, table):
        self.db.add_build(self.build)

        sess.return_value.refresh.assert_called_once_with(table.return_value)
        sess.return_value.expunge.assert_called_once_with(table.return_value)


class TestSQLAlchemyDBUpdateBuild(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBUpdateBuild, self).setup_method(method)
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
        table.id.__eq__.assert_called_once_with(self.build.ref.id)

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
            keys=('root_url',),
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
            keys=('root_url',),
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
            keys=('fqdn',),
            name=gh.return_value,
            fqdn=gh.return_value,
            active=True,
            busy=False,
            registered=False,
        )


class TestSQLAlchemyDBLockAgent(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBLockAgent, self).setup_method(method)
        self.db.set_agent_lock = mock.Mock()

    def test_call(self):
        self.db.lock_agent(self.build)
        self.db.set_agent_lock.assert_called_once_with(self.build, True)


class TestSQLAlchemyDBUnlockAgent(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBUnlockAgent, self).setup_method(method)
        self.db.set_agent_lock = mock.Mock()

    def test_call(self):
        self.db.unlock_agent(self.build)
        self.db.set_agent_lock.assert_called_once_with(self.build, False)


class TestSQLAlchemyDBSetAgentLock(SQLAlchemyDBBase):
    def assert_lock(self, session, table, locked):
        table.id.__eq__ = mock.Mock()
        self.db.set_agent_lock(self.build, locked)

        agent = session.return_value.query.return_value.get.return_value.agent

        assert agent.busy is locked
        session.return_value.add.assert_called_once_with(agent)

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_query_chain(self, session, table):
        self.db.set_agent_lock(self.build, True)

        query = session.return_value.query
        get = query.return_value.get

        query.assert_called_once_with(table)
        get.assert_called_once_with(self.build.ref.id)

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_agent_updated_to_locked(self, session, table):
        self.assert_lock(session, table, True)

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_agent_updated_to_unlocked(self, session, table):
        self.assert_lock(session, table, False)


class TestSQLAlchemyDBGetBuild(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBGetBuild, self).setup_method(method)
        self.build_id = 'phantom_moon'

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value(self, session, table):
        ret = self.db.get_build(self.build_id)
        assert ret is session.return_value.query.return_value.get.return_value

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_result_is_expunged(self, session, table):
        self.db.get_build(self.build_id)
        session.return_value.expunge_all.assert_called_once_with()


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

    def teardown_method(self, method):
        os.remove('test.db')

    def assert_vcs(self, session):
        assert session.query(VCSRoot).count() == 1

        vcs = session.query(VCSRoot).first()
        assert vcs.name == self.build.vcs.name
        assert vcs.root_url == self.build.vcs.root_url

    def assert_agent(self, session):
        assert session.query(Agent).count() == 1

        agent = session.query(Agent).first()
        assert agent.name == self.hostname
        assert agent.fqdn == self.hostname
        assert agent.active is True
        assert agent.busy is False
        assert agent.registered is False

    def assert_project(self, session):
        assert session.query(Project).count() == 1

        project = session.query(Project).first()
        assert project.name == self.build.vcs.get_project_name.return_value

    def assert_build(self, session):
        assert session.query(Build).count() == 1

        build = session.query(Build).first()
        assert build.success == self.success
        assert build.crashed == self.crashed
        assert build.status == self.status
        assert build.updated == self.now

    def test_get_vcs(self):
        self.build.vcs.name = 'oh sailor'
        self.build.vcs.root_url = 'fiona://extraordinary-machine.net'

        self.db.get_vcs(self.build)

        with in_session() as session:
            self.assert_vcs(session)

    @mock.patch('socket.gethostname')
    def test_get_agent(self, gh):
        self.hostname = 'shadow.cabinet'
        gh.return_value = self.hostname
        self.db.get_agent()

        with in_session() as session:
            self.assert_agent(session)

    def test_get_project(self):
        self.build.vcs.name = 'apathy divine'
        self.build.vcs.root_url = 'tokenring://wutheringheights.dk'
        self.build.vcs.get_project_name.return_value = 'mandatory/fun'

        self.db.get_project(self.build)

        with in_session() as session:
            self.assert_vcs(session)
            self.assert_project(session)

    @mock.patch('os.getenv')
    @mock.patch('socket.gethostname')
    def test_add_build(self, gh, getenv):
        self.success, self.crashed, self.status = True, False, 'hehe'
        self.now = datetime.datetime.now()

        self.username = 'fatmike'
        self.hostname = 'anarchy.camp'
        getenv.return_value = self.username
        gh.return_value = self.hostname

        self.build.default_db_kwargs.return_value = {
            'success': self.success,
            'crashed': self.crashed,
            'status': self.status,
            'updated': self.now,
        }

        self.build.vcs.name = 'apathy divine'
        self.build.vcs.root_url = 'tokenring://wutheringheights.dk'
        self.build.vcs.get_project_name.return_value = 'mandatory/fun'

        self.db.add_build(self.build)

        with in_session() as session:
            # Yay integration
            self.assert_build(session)
            self.assert_agent(session)
            self.assert_vcs(session)
            self.assert_project(session)
