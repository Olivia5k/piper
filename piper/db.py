import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship


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
