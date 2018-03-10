from datetime import datetime, timedelta
from unittest import mock
from uuid import uuid4

import pytest
import pytz
from asyncpg.exceptions import ForeignKeyViolationError

from app.connections.db import get_db_pool
from app.visitor.models import increment_counter

pytestmark = pytest.mark.asyncio


async def test_increment_error_no_user(db, event_loop):
    cookie = str(uuid4())
    user_mock = mock.MagicMock()
    user_mock.id = 0
    user_mock.timezone = 'UTC'
    with pytest.raises(ForeignKeyViolationError):
        await increment_counter(user_mock, cookie, '/')


async def test_increment_error_wrong_uuid(user):
    with pytest.raises(ValueError):
        await increment_counter(user, '', '/')


async def test_increment_success_increase(user, admin):
    pool = await get_db_pool()
    cookie = uuid4()
    await increment_counter(user, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 1
    visitor = visitors[0]
    assert visitor['cookie'] == cookie
    assert visitor['account_id'] == user.id
    tz = pytz.timezone(user.timezone)
    assert visitor['date'] == datetime.now(tz=tz).date()
    assert visitor['path'] == '/'
    assert visitor['hits'] == 1

    await increment_counter(user, cookie, '/')
    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 1
    visitor2 = visitors[0]
    assert visitor2['id'] == visitor['id']
    assert visitor2['hits'] == 2


async def test_increment_success_another_path(user, admin):
    pool = await get_db_pool()
    cookie = uuid4()
    await increment_counter(user, cookie, '/')
    await increment_counter(user, cookie, '/about/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1


async def test_increment_success_another_visitor(user, admin):
    pool = await get_db_pool()
    cookie = uuid4()
    await increment_counter(user, cookie, '/')
    cookie = uuid4()
    await increment_counter(user, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1


async def test_increment_success_another_account(user, admin):
    pool = await get_db_pool()
    cookie = uuid4()
    await increment_counter(user, cookie, '/')
    await increment_counter(admin, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1


async def test_increment_success_tomorrow(user, monkeypatch):
    pool = await get_db_pool()
    cookie = uuid4()
    await increment_counter(user, cookie, '/')

    tz = pytz.timezone(user.timezone)
    tomorrow = datetime.now(tz=tz) + timedelta(days=1)
    with mock.patch('app.visitor.models.datetime') as datetime_mock:
        datetime_mock.now.return_value = tomorrow
        await increment_counter(user, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1
