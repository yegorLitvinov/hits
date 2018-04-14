from http.cookies import SimpleCookie
from uuid import UUID, uuid4

import pytest

import ujson
from app.account.models import User
from app.conf import settings

pytestmark = pytest.mark.asyncio


async def test_wrong_method(client):
    response = await client.get('/api/account/login/')
    assert response.status == 405
    response = await client.get('/api/account/logout/')
    assert response.status == 405


async def test_login_empty_credentials(client):
    data = ujson.dumps({
        'password': '234442',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 400

    data = ujson.dumps({
        'email': '234442',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 400

    data = ujson.dumps({})
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 400


async def test_login_wrong_credentials(db, client):
    data = ujson.dumps({
        'email': 'admin',
        'password': 'r00t',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 404


async def test_unauthorized(client):
    response = await client.post('/api/account/check-auth/')
    assert response.status == 401
    cookies = SimpleCookie()
    cookies[settings.SESSION_COOKIE_NAME] = str(uuid4())
    response = await client.post('/api/account/check-auth/')
    assert response.status == 401


async def test_login_success(client, user):
    data = ujson.dumps({
        'email': user.email,
        'password': 'user',
    })
    response = await client.post('/api/account/login/', data=data)

    assert response.status == 200
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie
    assert cookie.value == str(UUID(cookie.value))
    resp_data = await response.json()
    assert resp_data == user.to_dict()

    response = await client.post('/api/account/check-auth/')
    assert response.status == 200


async def test_login_inactive_user(client, user):
    await user.update(is_active=False).apply()
    data = ujson.dumps({
        'email': user.email,
        'password': 'user',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 404
    with pytest.raises(KeyError):
        response.cookies[settings.SESSION_COOKIE_NAME]


async def test_logout_success(client, user, login):
    await login(user)
    response = await client.post('/api/account/logout/')
    assert response.status == 204
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie.value == ''


async def test_logout_error(db, client):
    response = await client.post('/api/account/logout/')
    assert response.status == 401
    with pytest.raises(KeyError):
        response.cookies[settings.SESSION_COOKIE_NAME]


async def test_patch_profile_success(client, user, login):
    await login(user)
    data = ujson.dumps({
        'timezone': 'Europe/Moscow',
    })
    response = await client.patch('/api/account/profile/', data=data)
    assert response.status == 200
    resp_data = await response.json()
    assert resp_data['timezone'] == 'Europe/Moscow'
    user = await User.get(user.id)
    assert user.timezone == 'Europe/Moscow'


async def test_patch_profile_error(client, user, login):
    await login(user)
    data = ujson.dumps({
        'timezone': 'Europe/Lipetsk',
    })
    response = await client.patch('/api/account/profile/', data=data)
    assert response.status == 400
    resp_data = await response.json()
    assert resp_data['timezone'] == ['Not a valid choice']
