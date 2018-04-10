from datetime import date, datetime
from uuid import UUID, uuid4

import pytest
import pytz

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
    await user.update(is_active=False).apply()
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

    visitor = await Visitor.query.gino.first()
    assert visitor.cookie == UUID(cookie.value)
    assert visitor.account_id == user.id
    tz = pytz.timezone(user.timezone)
    assert visitor.date == datetime.now(tz=tz).date()
    assert visitor.path == '/about/'
    assert visitor.hits == 2


async def test_hit_without_trailing_slash(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}',
    })
    assert response.status == 200
    visitor = await Visitor.query.gino.first()
    assert visitor.path == '/'
    assert visitor.hits == 1


async def test_hit_querystring(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}?param=value',
    })
    assert response.status == 200
    visitor = await Visitor.query.gino.first()
    assert visitor.path == '/'
    assert visitor.hits == 1


async def test_visitors_list(client, user, login):
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    v2 = await Visitor.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4(),
        hits=2,
    )
    v1 = await Visitor.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4(),
    )
    await login(user)
    response = await client.get('/api/visitors/', params={
        'filter_by': 'month',
        'date': now.strftime('%Y-%m-%d'),
        'offset': 0,
        'limit': 10,
        'order_by': 'date',
    })
    assert response.status == 200
    data = await response.json()
    assert len(data['data']) == data['total'] == 2
    assert data['data'][0]['id'] == v1.id
    assert data['data'][1]['id'] == v2.id
