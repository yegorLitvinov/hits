from datetime import datetime
from uuid import UUID

from src.settings import COOKIE_NAME

from .conftest import prepare_pool


async def test_wrong_url(db, loop, client):
    response = await client.get('/')
    assert response.status == 404
    response = await client.get('/visit/')
    assert response.status == 404


async def test_wrong_method(db, loop, client):
    response = await client.put('/visit/somekey')
    assert response.status == 405
    response = await client.post('/visit/somekey/')
    assert response.status == 405


async def test_wrong_credentials(db, loop, user, client):
    await prepare_pool(loop, user)
    response = await client.get('/visit/somekey')
    assert response.status == 404
    response = await client.get('/visit/b1df43e0-465b-41a2-942c-c46f274cd68f/')
    assert response.status == 404


async def test_inactive_user(db, loop, user, client):
    user.is_active = False
    await prepare_pool(loop, user)
    response = await client.get(f'/visit/{user.api_key}/')
    assert response.status == 404


async def test_2hits(db, loop, client, user):
    pool = await prepare_pool(loop, user)
    response = await client.get(f'/visit/{user.api_key}/', headers={
        'Referer': 'https://example.com/about/',
    })
    cookie = response.cookies[COOKIE_NAME]
    response = await client.get(f'/visit/{user.api_key}/', headers={
        'Referer': 'https://example.com/about/',
    })
    assert cookie
    assert cookie.value == str(UUID(cookie.value))

    async with pool.acquire() as conn:
        visitors = await conn.fetch('select * from visitor')
    assert len(visitors) == 1
    visitor = visitors[0]
    assert visitor['cookie'] == UUID(cookie.value)
    assert visitor['account_id'] == user.id
    assert visitor['date'] == datetime.now().date()
    assert visitor['path'] == '/about/'
    assert visitor['hits'] == 2
