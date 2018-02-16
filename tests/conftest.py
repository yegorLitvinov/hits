import asyncio
import os

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.account import User
from src.db import get_pool
from src.settings import DSN_KWARGS

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
    root_cursor.execute(f'create database {TEST_DBNAME} owner hits')

    hits_conn = psycopg2.connect(get_dsn())
    hits_cursor = hits_conn.cursor()

    schema = open(os.path.join(sql_dir, 'schema.sql')).read()
    try:
        hits_cursor.execute(schema)
        hits_conn.commit()
        yield
    finally:
        root_cursor.execute(f'REVOKE CONNECT ON DATABASE {TEST_DBNAME} FROM public')
        root_conn.commit()
        root_cursor.execute(
            'select pg_terminate_backend(pid) from pg_stat_activity '
            f'where datname=\'{TEST_DBNAME}\'',
        )
        root_conn.commit()
        # hits_cursor.close()
        # hits_conn.close()
        root_cursor.execute(f'drop database {TEST_DBNAME}')
        root_conn.commit()
        root_cursor.close()
        root_conn.close()


@pytest.yield_fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def pool(event_loop, db):
    p = await get_pool(event_loop)
    yield p
    await p.close()


# FIXME: db implicitly used in all tests
@pytest.fixture(autouse=True)
async def cleanup_db(pool):
    async with pool.acquire() as conn:
        await conn.execute('delete from account')
        await conn.execute('delete from hit')


@pytest.fixture
async def user():
    u = User(
        email='user@example.com',
        domain='example.com',
        is_active=True,
        is_superuser=False
    )
    u.set_password('user')
    await u.save()
    return u


@pytest.fixture
async def admin():
    u = User(
        email='admin@example.com',
        domain='superuser.com',
        is_active=True,
        is_superuser=True
    )
    u.set_password('admin')
    await u.save()
    return u
