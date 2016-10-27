import os

from migrate import exceptions as versioning_exceptions
from migrate.versioning import api as versioning_api
from migrate.versioning.repository import Repository
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log as logging
import sqlalchemy
from sqlalchemy.sql import null

from mgmt.db.sqlalchemy import api as db_session

INIT_VERSION = {}
INIT_VERSION['mgmt'] = 0
_REPOSITORY = {}



def get_engine(database='mgmt', context=None):
    return db_session.get_api_engine()


def db_sync(version=None, database='mgmt', context=None):
    if version is not None:
        try:
            version = int(version)
        except ValueError:
            raise exception.NovaException(_("version should be an integer"))

    current_version = db_version(database, context=context)
    repository = _find_migrate_repo(database)
    if version is None or version > current_version:
        return versioning_api.upgrade(get_engine(database, context=context),
                repository, version)
    else:
        return versioning_api.downgrade(get_engine(database, context=context),
                repository, version)


def db_version(database='mgmt', context=None):
    repository = _find_migrate_repo(database)
    try:
        return versioning_api.db_version(get_engine(database, context=context),
                                         repository)
    except versioning_exceptions.DatabaseNotControlledError as exc:
        meta = sqlalchemy.MetaData()
        engine = get_engine(database, context=context)
        meta.reflect(bind=engine)
        tables = meta.tables
        if len(tables) == 0:
            db_version_control(INIT_VERSION[database],
                               database,
                               context=context)
            return versioning_api.db_version(
                        get_engine(database, context=context), repository)
        else:
            raise Exception("Upgrade DB first.")


def db_initial_version(database='mgmt'):
    return INIT_VERSION[database]

def db_version_control(version=None, database='mgmt', context=None):
    repository = _find_migrate_repo(database)
    versioning_api.version_control(get_engine(database, context=context),
                                   repository,
                                   version)
    return version


def _find_migrate_repo(database='mgmt'):
    """Get the path for the migrate repository."""
    global _REPOSITORY
    rel_path = 'migrate_repo'
    if database == 'mgmt':
        rel_path = os.path.join('api_migrations', 'migrate_repo')
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        rel_path)
    assert os.path.exists(path)
    if _REPOSITORY.get(database) is None:
        _REPOSITORY[database] = Repository(path)
    return _REPOSITORY[database]