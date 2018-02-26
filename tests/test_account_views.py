from uuid import UUID, uuid4
import ujson
from http.cookies import SimpleCookie

import pytest
from app.conf import settings

pytestmark = pytest.mark.asyncio


async def test_wrong_method(event_loop, client):
    response = await client.get('/api/account/login/')
    assert response.status == 405
    response = await client.get('/api/account/logout/')
    assert response.status == 405


async def test_login_empty_credentials(db, event_loop, client):
    data = ujson.dumps({
        'email': None,
        'password': '234442',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 400


async def test_login_wrong_credentials(db, event_loop, client):
    data = ujson.dumps({
        'email': 'admin',
        'password': 'r00t',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 404


async def test_unauthorized(event_loop, client):
    response = await client.post('/api/account/check-auth/')
    assert response.status == 401
    cookies = SimpleCookie()
    cookies[settings.SESSION_COOKIE_NAME] = str(uuid4())
    response = await client.post('/api/account/check-auth/')
    assert response.status == 401


async def test_login_success(db, event_loop, client, user):
    data = ujson.dumps({
        'email': 'user@example.com',
        'password': 'user',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 200
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie
    assert cookie.value == str(UUID(cookie.value))

    response = await client.post('/api/account/check-auth/')
    assert response.status == 200


async def test_login_inactive_user(db, event_loop, client, user):
    user.is_active = False
    await user.save()
    data = ujson.dumps({
        'email': 'user@example.com',
        'password': 'user',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 404
    with pytest.raises(KeyError):
        response.cookies[settings.SESSION_COOKIE_NAME]


async def test_logout_success(db, event_loop, client, user):
    # TODO: async login fixture
    data = ujson.dumps({
        'email': 'user@example.com',
        'password': 'user',
    })
    response = await client.post('/api/account/login/', data=data)
    assert response.status == 200

    response = await client.post('/api/account/logout/')
    assert response.status == 204
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie.value == ''


async def test_logout_error(db, event_loop, client, user):
    # TODO: async login fixture
    response = await client.post('/api/account/logout/')
    assert response.status == 401
    with pytest.raises(KeyError):
        response.cookies[settings.SESSION_COOKIE_NAME]
