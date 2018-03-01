from datetime import datetime
from uuid import UUID

import pytest
from app.conf import settings
from app.visitor.models import Visitor

pytestmark = pytest.mark.asyncio


async def test_wrong_url(client):
    response = await client.get('/')
    assert response.status == 404
    response = await client.get('/api/visit/')
    assert response.status == 404


async def test_wrong_method(client):
    response = await client.put('/api/visit/somekey')
    assert response.status == 405
    response = await client.post('/api/visit/somekey/')
    assert response.status == 405


async def test_wrong_credentials(user, client):
    response = await client.get('/api/visit/somekey', headers={
        'Referer': f'https://{user.domain}/about/',
    })
    assert response.status == 404
    response = await client.get(
        '/api/visit/b1df43e0-465b-41a2-942c-c46f274cd68f/',
        headers={
            'Referer': f'https://{user.domain}/about/',
        }
    )
    assert response.status == 404


async def test_empty_referer(user, client):
    response = await client.get(f'/api/visit/{user.api_key}/')
    assert response.status == 400
    assert await response.text() == 'Empty referer'

    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': 'strange.addr',
    })
    assert response.status == 400
    assert await response.text() == 'Referer\'s domain is empty'


async def test_inactive_user(user, client):
    user.is_active = False
    await user.save()
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'https://{user.domain}/about/',
    })
    assert response.status == 404


async def test_2hits(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'https://{user.domain}/about/',
    })
    assert response.status == 200
    cookie = response.cookies[settings.VISITOR_COOKIE_NAME]
    assert cookie
    assert cookie.value == str(UUID(cookie.value))
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'https://{user.domain}/about/',
    })
    assert response.status == 200
    assert response.cookies.get(settings.VISITOR_COOKIE_NAME) is None

    visitor = await Visitor.get()
    assert visitor.cookie == UUID(cookie.value)
    assert visitor.account_id == user.id
    assert visitor.date == datetime.now().date()
    assert visitor.path == '/about/'
    assert visitor.hits == 2


async def test_hit_without_trailing_slash(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}',
    })
    assert response.status == 200
    visitor = await Visitor.get()
    assert visitor.path == '/'
    assert visitor.hits == 1


async def test_hit_querystring(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}?param=value',
    })
    assert response.status == 200
    visitor = await Visitor.get()
    assert visitor.path == '/'
    assert visitor.hits == 1
