import pytest
from asyncpg.exceptions import UndefinedColumnError

from app.account.models import User
from app.models import DoesNotExist, MultipleObjectsReturned

pytestmark = pytest.mark.asyncio


async def test_get_by_credentials(db, event_loop, user, admin):
    assert user.api_key != admin.api_key
    assert await User.get(email=user.email, password='user') == user
    with pytest.raises(DoesNotExist):
        assert await User.get(email='email@nonexist.com', password='user')
    with pytest.raises(DoesNotExist):
        await User.get(email=user.email, password='user234')
    with pytest.raises(DoesNotExist):
        await User.get(email=user.email, password='admin')

    assert await User.get(email=admin.email, password='admin') == admin
    with pytest.raises(DoesNotExist):
        await User.get(email='exii@test.com', password='admin')
    with pytest.raises(DoesNotExist):
        await User.get(email=admin.email, password='user234')
    with pytest.raises(DoesNotExist):
        await User.get(email=admin.email, password='user')


async def test_get_by_id(db, event_loop, user):
    assert await User.get(id=user.id) == user
    with pytest.raises(TypeError) as error:
        await User.get(id='dfdf')
    assert 'an integer is required' in str(error)
    with pytest.raises(DoesNotExist):
        await User.get(id=-1)
    with pytest.raises(DoesNotExist):
        await User.get(id=0)
    assert await User.get(id=user.id + 0.5) == user  # lol


async def test_get_errors(db, event_loop, user, admin):
    with pytest.raises(MultipleObjectsReturned):
        await User.get(is_active=True)
    with pytest.raises(UndefinedColumnError):
        await User.get(wrong_col=True)


async def test_filter(db, event_loop, user, admin):
    assert await User.filter(is_active=True) == [user, admin]
    assert await User.filter(is_active=False) == []
    assert await User.filter(is_superuser=True) == [admin]
    assert await User.filter(is_superuser=False) == [user]
    assert await User.filter() == [user, admin]
    assert await User.all() == [user, admin]


async def test_update_user(db, event_loop, user):
    user.set_password('new password')
    await user.save()
    user = await user.get_from_db()
    assert user.password == 'new password'
