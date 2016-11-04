import datetime

from sqlalchemy import (Column, Index, Integer, BigInteger, Enum, String,
                        schema, Unicode)
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float

BASE = declarative_base()


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')

class MgmtBase(models.TimestampMixin,
               models.ModelBase):
    metadata = None

    def __copy__(self):

        session = orm.Session()

        copy = session.merge(self, load=False)
        session.expunge(copy)
        return copy

class Service(BASE, MgmtBase):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    required = Column(String(10))


class DependentServices(BASE, MgmtBase):
    __tablename__ = "child_services"
    id = Column(Integer, primary_key=True)
    service_list = Column(String(255))


class ServiceStatus(BASE, MgmtBase):
    __tablename__ = "service_status"
    id = Column(Integer, primary_key=True)
    host = Column(String(255))
    port = Column(Integer)
    path = Column(String(255))
    use_https = Column(String(5))
    status = Column(String(50))
    last_updated = Column(DateTime, default = datetime.datetime.now())

class Request(BASE, MgmtBase):
    __tablename__ = "request"
    id = Column(Integer)
    req_content = Column(Text)
    version = Column(Integer)
    status = Column(String(50))
    update_time = Column(DateTime, default = datetime.datetime.now())
