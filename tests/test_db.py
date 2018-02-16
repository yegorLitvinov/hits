import pytest
from src.db import User

pytestmark = pytest.mark.asyncio


async def test_exists(pool, user, admin):
    assert await User.exists(user.email, 'user')
    assert not await User.exists(user.email, 'user234')
    assert not await User.exists(user.email, 'admin')

    assert await User.exists(admin.email, 'admin')
    assert not await User.exists(admin.email, 'user234')
    assert not await User.exists(admin.email, 'user')


async def test_empty_db(pool):
    async with pool.acquire() as conn:
        users = await conn.fetch('select * from account')
    assert len(users) == 0
