import os

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sanic import Sanic

from src.views import add_routes
from src.account import User
from src.settings import DSN_KWARGS
from src.db import get_pool

TEST_DBNAME = DSN_KWARGS['dbname'] + '_test'
DSN_KWARGS['dbname'] = TEST_DBNAME


def get_dsn(**kwargs):
    dsn_template = (
        'dbname={dbname} user={user} password={password} '
        'host={host} port={port}'
    )
    dsn_kwargs = DSN_KWARGS.copy()
    dsn_kwargs.update(kwargs)
    return dsn_template.format(**dsn_kwargs)


async def prepare(loop, user=None, admin=None):
    await get_pool(loop)
    if user:
        await user.save()
    if admin:
        await admin.save()


@pytest.fixture(scope='session')
def sql_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    return os.path.join(project_dir, 'sql')


@pytest.fixture(scope='session')
def db(sql_dir):
    root_conn = psycopg2.connect(
        get_dsn(dbname='postgres')
    )
    root_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    root_cursor = root_conn.cursor()
    root_cursor.execute(f'create database {TEST_DBNAME} owner {DSN_KWARGS["user"]}')

    metric_conn = psycopg2.connect(get_dsn())
    metric_cursor = metric_conn.cursor()

    schema = open(os.path.join(sql_dir, 'schema.sql')).read()
    try:
        metric_cursor.execute(schema)
        metric_conn.commit()
        yield
    finally:
        root_cursor.execute(f'REVOKE CONNECT ON DATABASE {TEST_DBNAME} FROM public')
        root_conn.commit()
        root_cursor.execute(
            'select pg_terminate_backend(pid) from pg_stat_activity '
            f'where datname=\'{TEST_DBNAME}\'',
        )
        root_conn.commit()
        root_cursor.execute(f'drop database {TEST_DBNAME}')
        root_conn.commit()
        root_cursor.close()
        root_conn.close()


@pytest.fixture
def execute(db):
    conn = psycopg2.connect(get_dsn())
    cursor = conn.cursor()

    def inner(query, *args):
        cursor.execute(query, *args)
        conn.commit()
        try:
            return cursor.fetchall()
        except psycopg2.ProgrammingError:
            pass
    yield inner

    cursor.close()
    conn.close()


# FIXME: db implicitly used in all tests
@pytest.fixture(autouse=True)
def cleanup_db(execute):
    execute('delete from account')
    execute('delete from visitor')


@pytest.fixture
def user(db):
    u = User(
        email='user@example.com',
        domain='example.com',
        is_active=True,
        is_superuser=False
    )
    u.set_password('user')
    return u


@pytest.fixture
def admin(db):
    u = User(
        email='admin@example.com',
        domain='superuser.com',
        is_active=True,
        is_superuser=True
    )
    u.set_password('admin')
    return u


@pytest.fixture
def app(loop):
    app = Sanic()
    add_routes(app)
    return app


@pytest.fixture
def client(app, loop, test_client):
    return loop.run_until_complete(test_client(app))
