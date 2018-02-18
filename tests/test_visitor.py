from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from asyncpg.exceptions import ForeignKeyViolationError

from src.visitor import increment_counter

from .conftest import prepare_pool


async def test_increment_error_no_user(db, loop):
    await prepare_pool(loop)
    cookie = str(uuid4())
    with pytest.raises(ForeignKeyViolationError):
        await increment_counter(0, cookie, '/')


async def test_increment_error_wrong_uuid(db, user, loop):
    await prepare_pool(loop, user)
    with pytest.raises(ValueError):
        await increment_counter(user.id, '', '/')


async def test_increment_success_increase(db, loop, user, admin):
    pool = await prepare_pool(loop, user, admin)
    cookie = uuid4()
    await increment_counter(user.id, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 1
    visitor = visitors[0]
    assert visitor['cookie'] == cookie
    assert visitor['account_id'] == user.id
    assert visitor['date'] == datetime.now().date()
    assert visitor['path'] == '/'
    assert visitor['hits'] == 1

    await increment_counter(user.id, cookie, '/')
    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 1
    visitor2 = visitors[0]
    assert visitor2['id'] == visitor['id']
    assert visitor2['hits'] == 2


async def test_increment_success_another_path(db, loop, user, admin):
    pool = await prepare_pool(loop, user, admin)
    cookie = uuid4()
    await increment_counter(user.id, cookie, '/')
    await increment_counter(user.id, cookie, '/about/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1


async def test_increment_success_another_visitor(db, loop, user, admin):
    pool = await prepare_pool(loop, user, admin)
    cookie = uuid4()
    await increment_counter(user.id, cookie, '/')
    cookie = uuid4()
    await increment_counter(user.id, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1


async def test_increment_success_another_account(db, loop, user, admin):
    pool = await prepare_pool(loop, user, admin)
    cookie = uuid4()
    await increment_counter(user.id, cookie, '/')
    await increment_counter(admin.id, cookie, '/')

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1


async def test_increment_success_tomorrow(db, loop, user, monkeypatch):
    pool = await prepare_pool(loop, user)
    cookie = uuid4()
    await increment_counter(user.id, cookie, '/')

    tomorrow = datetime.now() + timedelta(days=1)
    datetime_mock = MagicMock()
    datetime_mock.now.return_value = tomorrow
    import src.visitor
    monkeypatch.setattr(src.visitor, 'datetime', datetime_mock)

    await increment_counter(user.id, cookie, '/')
    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 2
    visitor2 = visitors[1]
    assert visitor2['cookie'] == cookie
    assert visitor2['hits'] == 1
