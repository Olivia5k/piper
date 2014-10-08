import datetime

from piper.db.db_sqlalchemy import SQLAlchemyManager
from piper.db.db_sqlalchemy import AgentManager
from piper.db.db_sqlalchemy import BuildManager
from piper.db.db_sqlalchemy import ProjectManager
from piper.db.db_sqlalchemy import VCSManager
from piper.db.db_sqlalchemy import PropertyManager
from piper.db.db_sqlalchemy import PropertyNamespaceManager
from piper.db.db_sqlalchemy import in_session

from piper.db.db_sqlalchemy import Agent
from piper.db.db_sqlalchemy import Build
from piper.db.db_sqlalchemy import Project
from piper.db.db_sqlalchemy import VCS
from piper.db.db_sqlalchemy import Property
from piper.db.db_sqlalchemy import PropertyNamespace

from test.utils import SQLATest
from test.utils import SQLAIntegration

import mock
import pytest


class BuildManagerTest(object):
    def setup_method(self, method):
        self.manager = BuildManager(mock.Mock())
        self.build = mock.Mock()


class ProjectManagerTest(object):
    def setup_method(self, method):
        self.manager = ProjectManager(mock.Mock())
        self.build = mock.Mock()


class AgentManagerTest(object):
    def setup_method(self, method):
        self.manager = AgentManager(mock.Mock())
        self.build = mock.Mock()


class VCSManagerTest(object):
    def setup_method(self, method):
        self.manager = VCSManager(mock.Mock())
        self.build = mock.Mock()


class PropertyManagerTest(object):
    def setup_method(self, method):
        self.manager = PropertyManager(mock.Mock())
        self.manager.db = mock.Mock()

        self.classes = []
        for x in range(2):
            cls = mock.MagicMock()
            prop = mock.Mock()
            prop.to_kwargs.return_value = {}
            cls.source.return_value.generate.return_value = [prop]

            self.classes.append(cls)


class PropertyNamespaceManagerTest(object):
    def setup_method(self, method):
        self.manager = PropertyNamespaceManager(mock.Mock())
        self.manager.db = mock.Mock()
        self.manager.get_or_create = mock.Mock()
        self.name = 'down.to.the.devil'


class TestBuildManagerAdd(BuildManagerTest):
    def setup_method(self, method):
        super(TestBuildManagerAdd, self).setup_method(method)
        self.build.default_db_kwargs.return_value = {'cave': 'canem'}
        self.manager.get_agent = mock.Mock()
        self.manager.get_project = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_object_ref_is_returned(self, sess, table):
        ret = self.manager.add(self.build)

        assert ret is table.return_value

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_instance_added_to_session(self, sess, table):
        self.manager.add(self.build)

        sess.return_value.add.assert_called_once_with(table.return_value)

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_instance_refreshed_and_expunged(self, sess, table):
        self.manager.add(self.build)

        sess.return_value.refresh.assert_called_once_with(table.return_value)
        sess.return_value.expunge.assert_called_once_with(table.return_value)


class TestBuildManagerUpdate(BuildManagerTest):
    def setup_method(self, method):
        super(TestBuildManagerUpdate, self).setup_method(method)
        self.extra = {'island in the sun': 'only way for things to come'}

    @mock.patch('piper.db.db_sqlalchemy.update')
    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_values(self, session, table, update):
        self.manager.update(self.build, **self.extra)

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

        self.manager.update(self.build, **self.extra)

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
        self.manager.update(self.build, **self.extra)

        stmt = update.return_value.where.return_value.values.return_value
        session.return_value.execute.assert_called_once_with(stmt)


class TestBuildManagerGet(BuildManagerTest):
    def setup_method(self, method):
        super(TestBuildManagerGet, self).setup_method(method)
        self.build_id = 'phantom_moon'

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value(self, session, table):
        ret = self.manager.get(self.build_id)
        assert ret is session.return_value.query.return_value.get.return_value

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_result_is_expunged(self, session, table):
        self.manager.get(self.build_id)
        session.return_value.expunge_all.assert_called_once_with()


class TestBuildManagerAll(BuildManagerTest):
    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value(self, session, table):
        ret = self.manager.all()
        assert ret is session.return_value.query.return_value.all.return_value

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_result_is_expunged(self, session, table):
        self.manager.all()
        session.return_value.expunge_all.assert_called_once_with()


class TestProjectManagerGet(ProjectManagerTest):
    def setup_method(self, method):
        super(TestProjectManagerGet, self).setup_method(method)
        self.manager.get_vcs = mock.Mock()
        self.manager.get_or_create = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value_is_project(self, session):
        ret = self.manager.get(self.build)
        assert ret is self.manager.get_or_create.return_value

    @mock.patch('piper.db.db_sqlalchemy.Project')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments(self, session, table):
        self.manager.get(self.build)

        self.manager.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            name=self.build.vcs.get_project_name.return_value,
            vcs=self.manager.db.vcs.get.return_value
        )


class TestAgentManagerGet(AgentManagerTest):
    def setup_method(self, method):
        super(TestAgentManagerGet, self).setup_method(method)
        self.manager.get_or_create = mock.Mock()

    @mock.patch('socket.gethostname')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value_is_agent(self, session, gh):
        ret = self.manager.get()
        assert ret is self.manager.get_or_create.return_value

    @mock.patch('socket.gethostname')
    @mock.patch('piper.db.db_sqlalchemy.Agent')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments(self, session, table, gh):
        self.manager.get()

        self.manager.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            keys=('fqdn',),
            expunge=False,
            name=gh.return_value,
            fqdn=gh.return_value,
            active=True,
            busy=False,
            registered=False,
        )


class TestAgentManagerLock(AgentManagerTest):
    def setup_method(self, method):
        super(TestAgentManagerLock, self).setup_method(method)
        self.manager.set_lock = mock.Mock()

    def test_call(self):
        self.manager.lock(self.build)
        self.manager.set_lock.assert_called_once_with(self.build, True)


class TestAgentManagerUnlock(AgentManagerTest):
    def setup_method(self, method):
        super(TestAgentManagerUnlock, self).setup_method(method)
        self.manager.set_lock = mock.Mock()

    def test_call(self):
        self.manager.unlock(self.build)
        self.manager.set_lock.assert_called_once_with(self.build, False)


class TestAgentManagerSetAgentLock(AgentManagerTest):
    def assert_lock(self, session, table, locked):
        table.id.__eq__ = mock.Mock()
        self.manager.set_lock(self.build, locked)

        agent = session.return_value.query.return_value.get.return_value.agent

        assert agent.busy is locked
        session.return_value.add.assert_called_once_with(agent)

    @mock.patch('piper.db.db_sqlalchemy.Build')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_query_chain(self, session, table):
        self.manager.set_lock(self.build, True)

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


class TestVCSManagerGet(VCSManagerTest):
    def setup_method(self, method):
        super(TestVCSManagerGet, self).setup_method(method)
        self.manager.get_or_create = mock.Mock()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value_is_vcs(self, session):
        ret = self.manager.get(self.build)
        assert ret is self.manager.get_or_create.return_value

    @mock.patch('piper.db.db_sqlalchemy.VCS')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments(self, session, table):
        self.manager.get(self.build)

        self.manager.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            expunge=False,
            keys=('root_url',),
            root_url=self.build.vcs.root_url,
            name=self.build.vcs.name,
        )

    @mock.patch('piper.db.db_sqlalchemy.VCS')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_get_or_create_arguments_with_expunge(self, session, table):
        self.manager.get(self.build, expunge=True)

        self.manager.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            expunge=True,
            keys=('root_url',),
            root_url=self.build.vcs.root_url,
            name=self.build.vcs.name,
        )


class TestPropertyManagerUpdate(PropertyManagerTest):
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_agent_is_gotten(self, session):
        self.manager.update(self.classes)
        self.manager.db.agent.get.assert_called_once_with(expunge=True)

    @mock.patch('piper.db.db_sqlalchemy.Property')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_deletion_query_chain(self, session, table):
        self.manager.update(self.classes)

        query = session.return_value.query
        filter = query.return_value.filter
        delete = filter.return_value.delete

        query.assert_called_once_with(table)
        assert filter.call_count == 1
        delete.assert_called_once_with()

    @mock.patch('piper.db.db_sqlalchemy.Property')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_property_namespace_retrieval(self, session, table):
        self.manager.update(self.classes)

        calls = [
            mock.call(self.classes[0].source.namespace),
            mock.call(self.classes[1].source.namespace),
        ]
        self.manager.db.property_namespace.get.assert_has_calls(calls)


class TestPropertyNamespaceManagerGet(PropertyNamespaceManagerTest):
    @mock.patch('piper.db.db_sqlalchemy.PropertyNamespace')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_without_session(self, session, table):
        self.manager.get_or_create = mock.Mock()
        ret = self.manager.get(self.name)

        assert ret is self.manager.get_or_create.return_value
        self.manager.get_or_create.assert_called_once_with(
            session.return_value,
            table,
            name=self.name,
            expunge=True,
        )

    @mock.patch('piper.db.db_sqlalchemy.PropertyNamespace')
    def test_with_session(self, table):
        self.session = mock.Mock()
        ret = self.manager.get(self.name, self.session)

        assert ret is self.manager.get_or_create.return_value
        self.manager.get_or_create.assert_called_once_with(
            self.session,
            table,
            name=self.name,
            expunge=True,
        )


class TestSQLAlchemyDBSetup(SQLATest):
    @mock.patch('piper.db.db_sqlalchemy.create_engine')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_setup(self, se, ce):
        self.db.setup(self.config)

        assert self.db.config is self.config
        ce.assert_called_once_with(self.config.raw['db']['host'])
        se.configure.assert_called_once_with(bind=ce.return_value)


class TestSQLAlchemyDBInit(SQLATest):
    def test_no_db(self):
        self.config.raw['db']['host'] = None

        with pytest.raises(AssertionError):
            self.db.init(self.config)

    def test_calls(self):
        host = 'sqlite:///'
        self.config.raw['db']['host'] = host
        self.db.handle_sqlite = mock.Mock()
        self.db.create_tables = mock.Mock()

        self.db.init(self.config)

        self.db.handle_sqlite.assert_called_once_with(host)
        self.db.create_tables.assert_called_once_with(
            host,
            echo=self.config.verbose,
        )


class TestSQLAlchemyDBHandleSqlite(SQLATest):
    @mock.patch('piper.utils.mkdir')
    @mock.patch('os.path.dirname')
    @mock.patch('os.path.exists')
    def test_sqlite_handling_creates_dir(self, exists, dirname, mkdir):
        self.config.db.host = 'sqlite:///amaranthine.db'
        exists.return_value = False

        self.db.handle_sqlite(self.config.host)
        mkdir.assert_called_once_with(dirname.return_value)


class TestSQLAlchemyDBCreateTables(SQLATest):
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


class TestSQLAlchemyDBSetupManagers(SQLATest):
    def test_set(self):
        table, manager = mock.Mock(), mock.Mock()
        table.__tablename__ = 'hehe'
        manager.__name__ = 'manager'

        self.db.tables = {
            table: manager
        }

        self.db.setup_managers()

        assert self.db.hehe is manager.return_value


class TestSQLAlchemyManagerGetOrCreate(object):
    def setup_method(self, method):
        self.manager = SQLAlchemyManager(mock.Mock())
        self.session = mock.Mock()
        self.model = mock.Mock()
        self.kwargs = {
            'life is a grave': 'i dig it',
            'stanton': 'creed',
        }
        self.keys = ['stanton']
        self.filtered_keys = {'stanton': 'creed'}
        self.filter = self.session.query.return_value.filter_by
        self.instance = self.filter.return_value.first.return_value

    def test_already_exists(self):
        ret = self.manager.get_or_create(
            self.session,
            self.model,
            **self.kwargs
        )

        assert ret is self.instance
        assert self.session.add.call_count == 0

    def test_does_not_exist(self):
        self.filter.return_value.first.return_value = None

        self.manager.get_or_create(self.session, self.model, **self.kwargs)

        self.model.assert_called_once_with(**self.kwargs)
        self.session.add.assert_called_once_with(self.model.return_value)

    def test_filter_kwargs_without_keys(self):
        self.manager.get_or_create(self.session, self.model, **self.kwargs)
        self.filter.assert_called_once_with(**self.kwargs)

    def test_filter_kwargs_with_keys(self):
        self.manager.get_or_create(
            self.session, self.model, keys=self.keys, **self.kwargs
        )
        self.filter.assert_called_once_with(**self.filtered_keys)

    def test_expungning_when_not_creating(self):
        self.filter.return_value.first.return_value = None
        self.manager.get_or_create(
            self.session, self.model, expunge=True,
        )
        self.session.expunge.assert_called_once_with(self.model.return_value)

    def test_expungning_when_creating(self):
        self.manager.get_or_create(
            self.session, self.model, expunge=True,
        )
        self.session.expunge.assert_called_once_with(self.instance)


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


class TestSQLiteIntegration(SQLAIntegration):
    def assert_vcs(self, session):
        assert session.query(VCS).count() == 1

        vcs = session.query(VCS).first()
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

        self.db.vcs.get(self.build)

        with in_session() as session:
            self.assert_vcs(session)

    @mock.patch('socket.gethostname')
    def test_get_agent(self, gh):
        self.hostname = 'shadow.cabinet'
        gh.return_value = self.hostname
        self.db.agent.get()

        with in_session() as session:
            self.assert_agent(session)

    def test_get_project(self):
        self.build.vcs.name = 'apathy divine'
        self.build.vcs.root_url = 'tokenring://wutheringheights.dk'
        self.build.vcs.get_project_name.return_value = 'mandatory/fun'

        self.db.project.get(self.build)

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

        self.db.build.add(self.build)

        with in_session() as session:
            # Yay integration
            self.assert_build(session)
            self.assert_agent(session)
            self.assert_vcs(session)
            self.assert_project(session)

    def test_update_properties_from_cli(self):
        from piper.cli.cmd_piperd import entry
        ret = entry(['prop', 'update'])

        assert ret == 0

        with in_session() as session:
            assert session.query(PropertyNamespace).count() == 1

            # I don't really know how to test for these. They are _supposed_ to
            # be different for all computers. The only real thing I can think
            # of is to actually check that some of them were created.
            assert session.query(Property).count() > 50
