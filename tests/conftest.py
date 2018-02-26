import asyncio
import os
from uuid import uuid4

import psycopg2
import pytest
from pytest_sanic.plugin import test_client as sanic_test_client
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sanic import Sanic
from redis import StrictRedis

from app.routes import add_routes
from app.account.models import User
from app.conf import settings
from app.connections.db import get_db_pool
from app.connections.redis import get_redis_pool

TEST_DBNAME = settings.DSN_KWARGS['dbname'] + '_test'
settings.DSN_KWARGS['dbname'] = TEST_DBNAME
settings.REDIS_KWARGS['db'] = 0


def get_dsn(**kwargs):
    dsn_template = (
        'dbname={dbname} user={user} password={password} '
        'host={host} port={port}'
    )
    dsn_kwargs = settings.DSN_KWARGS.copy()
    dsn_kwargs.update(kwargs)
    return dsn_template.format(**dsn_kwargs)


def pytest_addoption(parser):
    parser.addoption(
        "--reuse-db",
        action="store_true",
        default=False,
        help="Do not delete database after run."
    )


@pytest.fixture(scope='session')
def reuse_db(request):
    return request.config.getoption("--reuse-db")


@pytest.fixture(autouse=True)
async def connections(event_loop):
    db_pool = await get_db_pool(event_loop)
    redis_pool = await get_redis_pool(event_loop)
    yield
    await db_pool.close()
    redis_pool.close()
    await redis_pool.wait_closed()


@pytest.fixture(scope='session')
def session_event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def sql_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    return os.path.join(project_dir, 'app', 'migrations')


@pytest.fixture(scope='session')
def db(sql_dir, reuse_db):
    root_conn = psycopg2.connect(
        get_dsn(dbname='postgres')
    )
    root_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    root_cursor = root_conn.cursor()

    root_cursor.execute(f'SELECT 1 FROM pg_database WHERE datname = \'{TEST_DBNAME}\'')
    exists = root_cursor.fetchone()
    if not reuse_db:
        if exists:
            root_cursor.execute(f'drop database {TEST_DBNAME}')
        root_cursor.execute(f'create database {TEST_DBNAME} owner {settings.DSN_KWARGS["user"]}')
        root_conn.commit()
    elif not exists:
        root_cursor.execute(f'create database {TEST_DBNAME} owner {settings.DSN_KWARGS["user"]}')

    metric_conn = psycopg2.connect(get_dsn())
    metric_cursor = metric_conn.cursor()

    try:
        if not reuse_db or not exists:
            for filename in sorted(os.listdir(sql_dir)):
                if not filename.endswith('.sql'):
                    continue
                schema = open(os.path.join(sql_dir, filename)).read()
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
        if not reuse_db:
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


@pytest.fixture(scope='session')
def redis():
    r = StrictRedis(**settings.REDIS_KWARGS)
    yield r


# FIXME: db implicitly used in all tests
@pytest.fixture(autouse=True)
def cleanup_db(execute, redis):
    execute('delete from visitor')
    execute('delete from account')
    redis.flushdb()


@pytest.fixture
async def user(db, event_loop):
    u = User(
        email='user@example.com',
        domain='example.com',
        is_active=True,
        is_superuser=False,
        api_key=uuid4(),
    )
    u.set_password('user')
    await u.save()
    return u


@pytest.fixture
async def admin(db, event_loop):
    u = User(
        email='admin@example.com',
        domain='',
        is_active=True,
        is_superuser=True,
        api_key=uuid4(),
    )
    u.set_password('admin')
    await u.save()
    return u


@pytest.fixture
def test_client(event_loop):
    yield from sanic_test_client(event_loop)


@pytest.fixture
def app(event_loop):
    app = Sanic()
    add_routes(app)
    return app


@pytest.fixture
def client(app, event_loop, test_client):
    return event_loop.run_until_complete(test_client(app))
