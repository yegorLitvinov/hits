import os
from uuid import uuid4

import aioredis
import asyncpg
import pytest
from pytest_asyncio.plugin import event_loop as asyncio_event_loop
from pytest_sanic.plugin import test_client as sanic_test_client
from sanic import Sanic

from app.account.models import User
from app.conf import settings
from app.migrations.migrate import migrate
from app.routes import add_routes

TEST_DBNAME = settings.DSN_KWARGS['database'] + '_test'
settings.DSN_KWARGS['database'] = TEST_DBNAME
settings.REDIS_ADDR = 'redis://localhost/15'


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


@pytest.fixture(scope='session')
def event_loop(request):
    yield from asyncio_event_loop(request)


@pytest.fixture(scope='session')
async def db_conn(event_loop):
    db_conn = await asyncpg.connect(**settings.DSN_KWARGS)
    yield db_conn
    await db_conn.close()


@pytest.fixture(scope='session')
async def redis_conn(event_loop):
    redis_conn = await aioredis.create_connection(settings.REDIS_ADDR)
    yield redis_conn
    redis_conn.close()
    await redis_conn.wait_closed()


@pytest.fixture(scope='session')
def sql_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    return os.path.join(project_dir, 'app', 'migrations')


@pytest.fixture(scope='session')
async def db(sql_dir, reuse_db, event_loop):
    root_dsn_kwargs = settings.DSN_KWARGS.copy()
    root_dsn_kwargs['database'] = 'postgres'
    root_conn = await asyncpg.connect(**root_dsn_kwargs)

    exists = await root_conn.fetch(
        'SELECT 1 FROM pg_database WHERE datname = $1',
        TEST_DBNAME
    )

    async def create_db():
        await root_conn.execute('create database {} owner {}'.format(
            TEST_DBNAME,
            settings.DSN_KWARGS["user"],
        ))
    if not reuse_db:
        if exists:
            await root_conn.execute(f'drop database {TEST_DBNAME}')
        await create_db()
    elif not exists:
        await create_db()

    try:
        if not reuse_db or not exists:
            await migrate()
        yield
    finally:
        await root_conn.execute(f'REVOKE CONNECT ON DATABASE {TEST_DBNAME} FROM public')
        await root_conn.execute(
            'select pg_terminate_backend(pid) from pg_stat_activity where datname = $1',
            TEST_DBNAME,
        )
        if not reuse_db:
            await root_conn.execute(f'drop database {TEST_DBNAME}')
        await root_conn.close()


# FIXME: db implicitly used in all tests
@pytest.fixture(autouse=True)
async def cleanup_db(db, db_conn):
    await db_conn.execute('delete from visitor')
    await db_conn.execute('delete from account')


@pytest.fixture(autouse=True)
async def cleanup_redis(redis_conn):
    await redis_conn.execute('flushdb')


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


@pytest.fixture
def login(app, client, redis_conn):
    async def inner(user):
        session_cookie = str(uuid4())
        client.session.cookie_jar.update_cookies(
            {settings.SESSION_COOKIE_NAME: session_cookie}
        )
        redis_conn.execute('set', session_cookie, user.id)
    return inner
