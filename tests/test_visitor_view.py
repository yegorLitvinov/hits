from datetime import datetime
from uuid import UUID

import pytest
from app.conf import settings
from app.connections.db import get_db_pool

pytestmark = pytest.mark.asyncio


async def test_wrong_url(db, event_loop, client):
    response = await client.get('/')
    assert response.status == 404
    response = await client.get('/api/visit/')
    assert response.status == 404


async def test_wrong_method(db, event_loop, client):
    response = await client.put('/api/visit/somekey')
    assert response.status == 405
    response = await client.post('/api/visit/somekey/')
    assert response.status == 405


async def test_wrong_credentials(db, event_loop, user, client):
    response = await client.get('/api/visit/somekey', headers={
        'Referer': 'https://example.com/about/',
    })
    assert response.status == 404
    response = await client.get(
        '/api/visit/b1df43e0-465b-41a2-942c-c46f274cd68f/',
        headers={
            'Referer': 'https://example.com/about/',
        }
    )
    assert response.status == 404


async def test_empty_referer(db, event_loop, user, client):
    response = await client.get(f'/api/visit/{user.api_key}/')
    assert response.status == 400
    assert await response.text() == 'Referer\'s domain is empty'


async def test_inactive_user(db, event_loop, user, client):
    user.is_active = False
    await user.save()
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': 'https://example.com/about/',
    })
    assert response.status == 404


async def test_2hits(db, event_loop, client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': 'https://example.com/about/',  # TODO: querystring in referer
    })
    cookie = response.cookies[settings.VISITOR_COOKIE_NAME]
    assert cookie
    assert cookie.value == str(UUID(cookie.value))
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': 'https://example.com/about/',
    })
    assert response.cookies.get(settings.VISITOR_COOKIE_NAME) is None

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 1
    visitor = visitors[0]
    assert visitor['cookie'] == UUID(cookie.value)
    assert visitor['account_id'] == user.id
    assert visitor['date'] == datetime.now().date()
    assert visitor['path'] == '/about/'
    assert visitor['hits'] == 2
