from uuid import UUID, uuid4
import ujson
from http.cookies import SimpleCookie

import pytest
from app.conf import settings

from .conftest import prepare


async def test_wrong_method(loop, client):
    response = await client.get('/login/')
    assert response.status == 405


async def test_login_empty_credentials(db, loop, client):
    await prepare(loop)
    data = ujson.dumps({
        'email': None,
        'password': '234442',
    })
    response = await client.post('/login/', data=data)
    assert response.status == 400


async def test_login_wrong_credentials(db, loop, client):
    await prepare(loop)
    data = ujson.dumps({
        'email': 'admin',
        'password': 'r00t',
    })
    response = await client.post('/login/', data=data)
    assert response.status == 404


async def test_unauthorized(loop, client):
    response = await client.post('/check-auth/')
    assert response.status == 401
    cookies = SimpleCookie()
    cookies[settings.SESSION_COOKIE_NAME] = str(uuid4())
    response = await client.post('/check-auth/')
    assert response.status == 401


async def test_login_success(db, loop, client, user):
    await prepare(loop, user)
    data = ujson.dumps({
        'email': 'user@example.com',
        'password': 'user',
    })
    response = await client.post('/login/', data=data)
    assert response.status == 200
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie
    assert cookie.value == str(UUID(cookie.value))

    response = await client.post('/check-auth/')
    assert response.status == 200


async def test_logout_success(db, loop, client, user):
    # TODO: async login fixture
    await prepare(loop, user)
    data = ujson.dumps({
        'email': 'user@example.com',
        'password': 'user',
    })
    response = await client.post('/login/', data=data)
    assert response.status == 200

    response = await client.post('/logout/')
    assert response.status == 204
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie.value == ''


async def test_logout_error(db, loop, client, user):
    # TODO: async login fixture
    await prepare(loop, user)
    response = await client.post('/logout/')
    assert response.status == 401
    with pytest.raises(KeyError):
        response.cookies[settings.SESSION_COOKIE_NAME]
