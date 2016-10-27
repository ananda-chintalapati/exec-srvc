from migrate.changeset import UniqueConstraint
from migrate import ForeignKeyConstraint
from oslo_log import log as logging
from sqlalchemy import Boolean, BigInteger, Column, DateTime, Enum, Float
from sqlalchemy import dialects
from sqlalchemy import ForeignKey, Index, Integer, MetaData, String, Table
from sqlalchemy import Text
from sqlalchemy.types import NullType


def MediumText():
    return Text().with_variant(dialects.mysql.MEDIUMTEXT(), 'mysql')

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    service = Table('service', meta,
                    Column('id', Integer, primary_key=True),
                    Column('name', String(100)),
                    Column('required', String(10)))

    child_services = Table('child_services', meta,
                           Column('id', Integer),
                           Column('service_list'), String(255))

    service_status = Table('service_status', meta,
                           Column('id',Integer, primary_key=True),
                           Column('host', String(255)),
                           Column('port', Integer),
                           Column('path', String(255)),
                           Column('use_https', String(5)),
                           Column('status', String(50)),
                           Column('last_updated', DateTime))

    request = Table('request', meta,
                    Column('id', Integer),
                    Column('req_content', Text),
                    Column('version', Integer),
                    Column('status', String(50)),
                    Column('update_time', DateTime))