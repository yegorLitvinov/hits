import pytest
from asyncpg.exceptions import DataError

from app.account.models import User, encrypt_password

pytestmark = pytest.mark.asyncio


async def test_get_by_id(user, admin):
    assert (await User.get(user.id)).id == user.id
    with pytest.raises(DataError) as error:
        await User.get('dfdf')
    assert 'an integer is required' in str(error)
    assert await User.get(-1) is None
    await User.get(0) is None
    assert (await User.get(user.id + 0.7)).id == user.id  # lol


async def test_filter(user, admin):
    users = await User.query.where(User.is_active==True).gino.all()  # noqa
    assert list(map(lambda u: u.id, users)) == [user.id, admin.id]
    assert await User.query.where(User.is_active==False).gino.all() == []  # noqa
    users = await User.query.where(User.is_superuser==True).gino.all()  # noqa
    assert list(map(lambda u: u.id, users)) == [admin.id]
    users = await User.query.where(User.is_superuser==False).gino.all()  # noqa
    assert list(map(lambda u: u.id, users)) == [user.id]
    users = await User.query.gino.all()
    assert list(map(lambda u: u.id, users)) == [user.id, admin.id]


async def test_update_password(user):
    await user.update(password=encrypt_password('new password')).apply()
    user = await User.get(user.id)
    assert user.verify_password('new password')
