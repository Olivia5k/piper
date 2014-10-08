import os
import datetime
import socket
import contextlib
import json
import logbook

from piper import utils

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import update
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from piper.db.core import Database


Base = declarative_base()
Session = sessionmaker()


class SQLAlchemyManager(object):
    def __init__(self, db):
        self.db = db

        self.log = logbook.Logger(self.__class__.__name__)

    def get_or_create(self, session, model, expunge=False, keys=(), **kwargs):
        """
        Get or create an object.

        A filter is done on the model with `kwargs`. If `keys` are specified,
        only those keys will be used to do the filtering.

        If `expunge` is True, the created object is detached from the session.
        This is used if one get_or_create call calls another for its arguments
        since the different calls would get different sessions.

        """

        filter = kwargs
        if keys:
            filter = dict((k, v) for k, v in kwargs.items() if k in keys)

        instance = session.query(model).filter_by(**filter).first()
        if not instance:
            instance = model(**kwargs)
            session.add(instance)

        if expunge:
            session.expunge(instance)

        return instance


class Agent(Base):
    __tablename__ = 'agent'

    id = Column(Integer(), primary_key=True)
    fqdn = Column(String(255))
    name = Column(String(255))
    active = Column(Boolean())
    busy = Column(Boolean())
    registered = Column(Boolean())
    properties = relationship('Property')
    created = Column(DateTime(), default=utils.now)
    last_seen = Column(DateTime(), default=utils.now)


class AgentManager(SQLAlchemyManager):
    def get(self, expunge=False):
        with in_session() as session:
            name = socket.gethostname()
            agent = self.get_or_create(
                session,
                Agent,
                expunge=expunge,
                keys=('fqdn',),
                name=name,
                fqdn=name,  # XXX
                active=True,
                busy=False,
                registered=False,
            )

            return agent

    def lock(self, build):
        self.set_lock(build, True)

    def unlock(self, build):
        self.set_lock(build, False)

    def set_lock(self, build, locked):
        with in_session() as session:
            agent = session.query(Build).get(build.ref.id).agent
            agent.busy = locked

            session.add(agent)


class Build(Base):
    __tablename__ = 'build'

    id = Column(Integer(), primary_key=True)
    agent = relationship('Agent')
    agent_id = Column(Integer(), ForeignKey('agent.id'))
    project = relationship('Project')
    project_id = Column(Integer(), ForeignKey('project.id'))

    user = Column(String(255))
    success = Column(Boolean())
    crashed = Column(Boolean())
    status = Column(String(255))
    started = Column(DateTime(), default=utils.now)
    updated = Column(DateTime(), default=utils.now)
    ended = Column(DateTime())


class BuildManager(SQLAlchemyManager):
    def add(self, build):
        with in_session() as session:
            instance = Build(
                agent=self.db.agent.get(),
                project=self.db.project.get(build),
                user=os.getenv('USER'),
                **build.default_db_kwargs()
            )

            # Flush the object to save it.
            # Refresh it so that it get autogenerated fields (id
            # Expunge it so that it can be used by other sessions.
            session.add(instance)
            session.flush()
            session.refresh(instance)
            session.expunge(instance)

            return instance

    def update(self, build, **extra):
        with in_session() as session:
            values = build.default_db_kwargs()
            values.update(extra)

            stmt = update(Build).where(Build.id == build.ref.id).values(values)
            session.execute(stmt)

    def get(self, build_id):
        with in_session() as session:
            build = session.query(Build).get(build_id)
            if build is not None:
                # Aight, so this is obviously bad and wrong.
                # How do load in one query? Halp!
                build.agent.properties
                build.project.vcs

                session.expunge_all()
            return build

    def all(self):
        with in_session() as session:
            builds = session.query(Build).all()
            for build in builds:  # pragma: nocover
                build.agent.properties
                build.project.vcs

            session.expunge_all()
            return builds


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    vcs = relationship('VCS')
    vcs_id = Column(Integer(), ForeignKey('vcs.id'))
    created = Column(DateTime(), default=utils.now)


class ProjectManager(SQLAlchemyManager):
    def get(self, build):
        with in_session() as session:
            project = self.get_or_create(
                session,
                Project,
                name=build.vcs.get_project_name(),
                vcs=self.db.vcs.get(build, expunge=True),
            )

            return project


class VCS(Base):
    __tablename__ = 'vcs'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    root_url = Column(String(255))
    created = Column(DateTime(), default=utils.now)


class VCSManager(SQLAlchemyManager):
    def get(self, build, expunge=False):
        with in_session() as session:
            vcs = self.get_or_create(
                session,
                VCS,
                expunge=expunge,
                keys=('root_url',),
                root_url=build.vcs.root_url,
                name=build.vcs.name,
            )

        return vcs


class Property(Base):
    __tablename__ = 'property'

    id = Column(Integer(), primary_key=True)
    agent = relationship('Agent')
    agent_id = Column(Integer(), ForeignKey('agent.id'))
    namespace = relationship('PropertyNamespace')
    namespace_id = Column(Integer(), ForeignKey('property_namespace.id'))
    key = Column(String(255))
    value = Column(String(255))
    created = Column(DateTime(), default=utils.now)


class PropertyManager(SQLAlchemyManager):
    def update(self, classes):
        self.log.info('Updating properties')

        with in_session() as session:
            agent = self.db.agent.get(expunge=True)

            # Clear existing properties.
            query = session.query(Property).filter(Property.agent == agent)
            query.delete()
            self.log.debug('Cleared old properties')

            for prop_class in classes:
                prop_source = prop_class.source
                prop_source.log.info('Loading properties')
                prop_source.ns = self.db.property_namespace.get(
                    prop_source.namespace
                )

                for prop in prop_source.generate():
                    prop_source.log.debug(str(prop))

                    obj = Property(**prop.to_kwargs(
                        agent=agent,
                        namespace=prop_source.ns,
                    ))
                    session.add(obj)

                prop_source.log.info('Properties loaded')

            self.log.info('Property updating complete')


class PropertyNamespace(Base):
    __tablename__ = 'property_namespace'

    id = Column(Integer(), primary_key=True)
    properties = relationship('Property')
    name = Column(String(255))
    created = Column(DateTime(), default=utils.now)


class PropertyNamespaceManager(SQLAlchemyManager):
    def get(self, name, session=None):
        kwargs = {
            'name': name,
            'expunge': True,
        }
        if session is not None:
            ret = self.get_or_create(session, PropertyNamespace, **kwargs)
        else:
            with in_session() as session:
                ret = self.get_or_create(session, PropertyNamespace, **kwargs)

        return ret


@contextlib.contextmanager
def in_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class SQLAlchemyDB(Database):
    tables = {
        Agent: AgentManager,
        Build: BuildManager,
        Project: ProjectManager,
        VCS: VCSManager,
        Property: PropertyManager,
        PropertyNamespace: PropertyNamespaceManager,
    }

    sqlite = 'sqlite:///'

    def setup(self, config):
        self.config = config
        self.engine = create_engine(config.raw['db']['host'])
        Session.configure(bind=self.engine)

        self.setup_managers()

    def init(self, config):
        host = config.raw['db']['host']
        assert host is not None, 'No database configured'

        if host.startswith(self.sqlite):
            self.handle_sqlite(host)

        self.log.info('Creating tables for {0}'.format(host))
        self.create_tables(host, echo=config.verbose)

    def setup_managers(self):
        for cls, man in self.tables.items():
            table = cls.__tablename__
            self.log.debug(
                'Creating manager {0} as db.{1}'.format(man.__name__, table)
            )

            # Initialize the manager with this db as first argument. That way
            # they can all access each other in a clean way.
            instance = man(self)
            setattr(self, table, instance)

    def handle_sqlite(self, host):
        target = os.path.dirname(host.replace(self.sqlite, ''))
        if target and not os.path.exists(target):
            self.log.debug('Creating SQLite dir {0}'.format(target))
            utils.mkdir(target)

    def create_tables(self, host, echo=False):
        engine = create_engine(host, echo=echo)
        self.log.debug('Engine created')

        Session.configure(bind=engine)
        self.log.debug('Session configured')

        for table in self.tables:
            self.log.debug('Creating table `{0}`'.format(table.__tablename__))
            table.metadata.bind = engine
            table.metadata.create_all()

        self.log.info('Database initialization complete.')

    @property
    def json_settings(self):  # pragma: nocover
        return {
            'cls': AlchemyEncoder,
            'check_circular': False,
        }


class AlchemyEncoder(json.JSONEncoder):  # pragma: nocover
    cache = utils.LimitedSizeDict(size_limit=1000)

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            if obj in self.cache:
                return self.cache[obj]

            fields = {}
            for field in dir(obj):
                if not field.startswith('_') and field != 'metadata' \
                        and not field.endswith('_id'):
                    fields[field] = obj.__getattribute__(field)

            self.cache[obj] = fields
            return fields

        elif isinstance(obj, datetime.datetime):
            return str(obj.isoformat())

        return json.JSONEncoder.default(self, obj)
