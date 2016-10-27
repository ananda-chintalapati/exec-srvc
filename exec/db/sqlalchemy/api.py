import collections
import copy
import datetime
import functools
import inspect
import sys


import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import MetaData
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import joinedload_all
from sqlalchemy.orm import noload
from sqlalchemy.orm import undefer
from sqlalchemy.schema import Table
from sqlalchemy import sql
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import UpdateBase
from sqlalchemy.sql import false
from sqlalchemy.sql import func
from sqlalchemy.sql import null
from sqlalchemy.sql import true


main_context_manager = enginefacade.transaction_context()
api_context_manager = enginefacade.transaction_context()


def _get_db_conf(conf_group, connection=None):
    kw = dict(
        connection=connection or conf_group.connection,
        slave_connection=conf_group.slave_connection,
        sqlite_fk=False,
        __autocommit=True,
        expire_on_commit=False,
        mysql_sql_mode=conf_group.mysql_sql_mode,
        idle_timeout=conf_group.idle_timeout,
        connection_debug=conf_group.connection_debug,
        max_pool_size=conf_group.max_pool_size,
        max_overflow=conf_group.max_overflow,
        pool_timeout=conf_group.pool_timeout,
        sqlite_synchronous=conf_group.sqlite_synchronous,
        connection_trace=conf_group.connection_trace,
        max_retries=conf_group.max_retries,
        retry_interval=conf_group.retry_interval)
    return kw


def _context_manager_from_context(context):
    if context:
        try:
            return context.db_connection
        except AttributeError:
            pass


def configure(conf):
    main_context_manager.configure(**_get_db_conf(conf.database))
    api_context_manager.configure(**_get_db_conf(conf.api_database))


def create_context_manager(connection=None):
    """Create a database context manager object.
    : param connection: The database connection string
    """
    ctxt_mgr = enginefacade.transaction_context()
    ctxt_mgr.configure(**_get_db_conf(CONF.database, connection=connection))
    return ctxt_mgr


def get_context_manager(context):
    """Get a database context manager object.
    :param context: The request context that can contain a context manager
    """
    return _context_manager_from_context(context) or main_context_manager


def get_engine(use_slave=False, context=None):
    """Get a database engine object.
    :param use_slave: Whether to use the slave connection
    :param context: The request context that can contain a context manager
    """
    ctxt_mgr = _context_manager_from_context(context) or main_context_manager
    return ctxt_mgr.get_legacy_facade().get_engine(use_slave=use_slave)


def get_api_engine():
    return api_context_manager.get_legacy_facade().get_engine()

def model_query(context, model,
                args=None,
                read_deleted=None,
                project_only=False):
    """Query helper that accounts for context's `read_deleted` field.
    :param context:     NovaContext of the query.
    :param model:       Model to query. Must be a subclass of ModelBase.
    :param args:        Arguments to query. If None - model is used.
    :param read_deleted: If not None, overrides context's read_deleted field.
                        Permitted values are 'no', which does not return
                        deleted values; 'only', which only returns deleted
                        values; and 'yes', which does not filter deleted
                        values.
    :param project_only: If set and context is user-type, then restrict
                        query to match the context's project_id. If set to
                        'allow_none', restriction includes project_id = None.
    """



    query = sqlalchemyutils.model_query(
        model, context.session, args, **query_kwargs)

    return query

def get_service_list():
    query = model_query(context, models.Service)

    result = query.all()
    if not result:
        #raise Exception('Services not found')

    return result

def get_service_status(service_id):
    query = model_query(context, models.ServiceStatus).filter_by(name=service_id)

    result = query.first()
    if not result:
        #raise exception.ServiceNotFound(service_id=service_id)

    return result

def get_dependent_service_list(service_id):
    query = model_query(context, models.DependentServices).filter_by(name=service_id)

    result = query.first()
    if not result:
        #raise exception.ServiceNotFound(service_id=service_id)

    return result

def update_service_status(service_name):
    return IMPL.update_service_status(service_name)

def update_dependent_service_list(service_name, **kw):
    return IMPL.update_dependent_service_list(service_name, **kw)

def create_service(service_name, **kw):
    return IMPL.create_service(service_name, **kw)

def create_request(**req):
    return IMPL.create_request(**req)

def update_request(**req):
    return IMPL.update_request(**req)

def get_request(request_id):
    query = model_query(context, models.Request).filter_by(name=request_id)

    result = query.first()
    if not result:
        #raise exception.ServiceNotFound(service_id=service_id)

    return result

def get_all_requests():
    query = model_query(context, models.Request)

    result = query.first()
    if not result:
        #raise exception.ServiceNotFound(service_id=service_id)

    return result
