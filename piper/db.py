import os
import datetime

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

from piper import utils

import logbook


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


class DbCLI(object):
    tables = (Agent, Build, Project, VCSRoot, Property, PropertyNamespace)

    def __init__(self):
        self.log = logbook.Logger(self.__class__.__name__)

    def compose(self, parser):
        db = parser.add_parser('db', help='Perform database tasks')

        sub = db.add_subparsers(help='Database commands', dest="db_command")
        sub.add_parser('init', help='Run CREATE TABLE statements')

        return 'db', self.run

    def run(self, ns, config):
        self.init(ns, config)

        return 0

    def init(self, ns, config):
        host = config.db.host
        assert host is not None, 'No database configured'

        # SQLite needs a full path that might be relative. This allows to
        # specify {PWD} in the config string and let that be propagated here
        token = 'sqlite:///'
        if host.startswith(token):
            host = host.format(PWD=os.getenv('PWD'))
            self.log.info('Using {0} as host'.format(host))

            target = os.path.dirname(host.replace(token, ''))
            if not os.path.exists(target):
                self.log.debug('Creating {0}'.format(target))
                utils.mkdir(target)

        engine = create_engine(config.db.host, echo=ns.verbose)
        self.log.debug('Engine created')

        Session.configure(bind=engine)
        self.log.debug('Session configured')

        for table in self.tables:
            self.log.debug('Creating table {0}'.format(table.__tablename__))
            table.metadata.bind = engine
            table.metadata.create_all()

        self.log.info('Database initialization complete.')
