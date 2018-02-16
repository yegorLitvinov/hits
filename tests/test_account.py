import pytest

from src.account import User

pytestmark = pytest.mark.asyncio


async def test_get_by_credentials(pool, user, admin):
    assert await User.get_by_credentials(user.email, 'user') == user
    assert await User.get_by_credentials('email@nonexist.com', 'user') is None
    assert await User.get_by_credentials(user.email, 'user234') is None
    assert await User.get_by_credentials(user.email, 'admin') is None

    assert await User.get_by_credentials(admin.email, 'admin') == admin
    assert await User.get_by_credentials('exii@test.com', 'admin') is None
    assert await User.get_by_credentials(admin.email, 'user234') is None
    assert await User.get_by_credentials(admin.email, 'user') is None

    assert user.api_key != admin.api_key


async def test_empty_db(pool):
    async with pool.acquire() as conn:
        users = await conn.fetch('select * from account')
    assert len(users) == 0


async def test_get_by_id(pool, user, admin):
    assert await User.get_by_id(user.id) == user
    with pytest.raises(TypeError) as error:
        await User.get_by_id('dfdf')
    assert 'an integer is required' in str(error)
    assert await User.get_by_id(-1) is None
    assert await User.get_by_id(0) is None
    assert await User.get_by_id(user.id + 0.5) == user  # lol
