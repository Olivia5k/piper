import os
import datetime
import socket
import contextlib

from piper import utils

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from piper.db.core import DatabaseBase


Base = declarative_base()
Session = sessionmaker()


class Agent(Base):
    __tablename__ = 'agent'

    id = Column(Integer(), primary_key=True)
    fqdn = Column(String(255))
    name = Column(String(255))
    active = Column(Boolean())
    busy = Column(Boolean())
    registered = Column(Boolean())
    properties = relationship('Property')
    created = Column(DateTime, default=datetime.datetime.now)
    last_seen = Column(DateTime, default=datetime.datetime.now)


class Build(Base):
    __tablename__ = 'build'

    id = Column(Integer(), primary_key=True)
    agent = relationship('Agent')
    agent_id = Column(Integer, ForeignKey('agent.id'))
    project = relationship('Project')
    project_id = Column(Integer, ForeignKey('project.id'))

    user = Column(String(255))
    success = Column(Boolean())
    crashed = Column(Boolean())
    status = Column(String(255))
    started = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now)
    ended = Column(DateTime)


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    vcs = relationship('VCSRoot')
    vcs_id = Column(Integer, ForeignKey('vcs_root.id'))
    created = Column(DateTime, default=datetime.datetime.now)


class VCSRoot(Base):
    __tablename__ = 'vcs_root'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    root_url = Column(String(255))
    created = Column(DateTime, default=datetime.datetime.now)


class Property(Base):
    __tablename__ = 'property'

    id = Column(Integer(), primary_key=True)
    agent_id = Column(Integer, ForeignKey('agent.id'))
    namespace_id = Column(Integer, ForeignKey('property_namespace.id'))
    key = Column(String(255))
    value = Column(String(255))
    created = Column(DateTime, default=datetime.datetime.now)


class PropertyNamespace(Base):
    __tablename__ = 'property_namespace'

    id = Column(Integer(), primary_key=True)
    properties = relationship('Property')
    name = Column(String(255))
    created = Column(DateTime, default=datetime.datetime.now)


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


class SQLAlchemyDB(DatabaseBase):
    tables = (Agent, Build, Project, VCSRoot, Property, PropertyNamespace)
    sqlite = 'sqlite://'

    def setup(self, config):
        self.config = config
        self.engine = create_engine(config.db.host)
        Session.configure(bind=self.engine)

    def init(self, ns, config):
        host = config.db.host
        assert host is not None, 'No database configured'

        if host.startswith(self.sqlite) and host != self.sqlite:
            self.handle_sqlite(host)

        self.log.info('Creating tables for {0}'.format(host))
        self.create_tables(host, echo=ns.verbose)

    def handle_sqlite(self, host):
        target = os.path.dirname(host.replace(self.sqlite, ''))

        if not os.path.exists(target):
            self.log.debug('Creating {0}'.format(target))
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

    def get_or_create(self, session, model, expunge=False, **kwargs):
        # http://stackoverflow.com/questions/2546207/
        instance = session.query(model).filter_by(**kwargs).first()
        if not instance:
            instance = model(**kwargs)
            session.add(instance)

        if expunge:
            session.expunge(instance)

        return instance

    def add_build(self, build):
        with in_session() as session:
            instance = Build(
                agent=self.get_agent(),
                project=self.get_project(build),
                user=os.getenv('USER'),
                **build.default_db_kwargs()
            )
            session.add(instance)

            return instance.id

    def update_build(self, build, **extra):
        with in_session() as session:
            values = build.default_db_kwargs()
            values.update(extra)

            stmt = update(Build).where(Build.id == build.id).values(values)
            session.execute(stmt)

    def get_project(self, build):
        """
        Lazily get the project.

        Create the project if it does not exist. If the VCS root for the
        project does not exist, create that too.

        """

        with in_session() as session:
            project = self.get_or_create(
                session,
                Project,
                name=build.vcs.get_project_name(),
                vcs=self.get_vcs(build, expunge=True),
            )

            return project

    def get_vcs(self, build, expunge=False):
        with in_session() as session:
            vcs = self.get_or_create(
                session,
                VCSRoot,
                expunge=expunge,
                root_url=build.vcs.root_url,
                name=build.vcs.name,
            )

        return vcs

    def get_agent(self):
        with in_session() as session:
            name = socket.gethostname()
            agent = self.get_or_create(
                session,
                Agent,
                name=name,
                fqdn=name,  # XXX
                active=True,
                busy=False,
                registered=False,
            )

            return agent
