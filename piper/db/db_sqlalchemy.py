import os
import datetime

from piper import utils

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
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
    busy = Boolean()
    properties = relationship('Property')
    created = Column(DateTime, default=datetime.datetime.now)
    last_seen = Column(DateTime, default=datetime.datetime.now)


class Build(Base):
    __tablename__ = 'build'

    id = Column(Integer(), primary_key=True)
    agent = relationship('Agent')
    project = relationship('Project')
    success = Boolean()
    started = Column(DateTime, default=datetime.datetime.now)
    ended = Column(DateTime)


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    vcs = relationship('VCSRoot')
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


def in_session(func):
    """
    Decorator that gives a session scope to the function

    """

    def inner(self, *args, **kwargs):
        session = Session()
        ret = func(session, *args, **kwargs)
        session.close()
        return ret

    return inner


class SQLAlchemyDB(DatabaseBase):
    tables = (Agent, Build, Project, VCSRoot, Property, PropertyNamespace)
    sqlite = 'sqlite:///'

    def setup(self, config):
        self.config = config
        self.engine = create_engine(config.db.host)
        Session.configure(bind=self.engine)

    def init(self, ns, config):
        host = config.db.host
        assert host is not None, 'No database configured'

        if host.startswith(self.sqlite):
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
