from datetime import datetime
from ipaddress import IPv4Address
from uuid import UUID, uuid4

import pytest
import pytz
from fake_useragent import UserAgent

from app.conf import settings
from app.visit.models import Visit

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

    visits = await Visit.query.gino.all()
    assert len(visits) == 2
    assert all([visit.cookie == UUID(cookie.value) for visit in visits])
    assert all([visit.account_id == user.id for visit in visits])
    tz = pytz.timezone(user.timezone)
    assert all([
        (
            visit.date.replace(second=0, microsecond=0) ==
            datetime.now(tz=tz).replace(second=0, microsecond=0)
        )
        for visit in visits
    ])
    assert all([visit.path == '/about/' for visit in visits])


async def test_hit_without_trailing_slash(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}',
    })
    assert response.status == 200
    visits = await Visit.query.gino.all()
    assert len(visits) == 1
    assert visits[0].path == '/'


async def test_visit_user_agent(client, user):
    ua = UserAgent()
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}',
        'User-Agent': ua.random,
    })
    assert response.status == 200
    visits = await Visit.query.gino.all()
    assert len(visits) == 1
    assert visits[0].path == '/'
    assert visits[0].user_agent


async def test_visit_user_agent_no_header(client, user):
    response = await client.get(
        f'/api/visit/{user.api_key}/',
        headers={'Referer': f'http://{user.domain}'},
        skip_auto_headers={'USER-AGENT'},
    )
    assert response.status == 200
    visits = await Visit.query.gino.all()
    assert len(visits) == 1
    assert visits[0].path == '/'
    assert visits[0].user_agent['ua_string'] == ''


async def test_hit_querystring(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}?param=value',
    })
    assert response.status == 200
    visits = await Visit.query.gino.all()
    assert len(visits) == 1
    assert visits[0].path == '/'


async def test_real_ip(client, user):
    response = await client.get(f'/api/visit/{user.api_key}/', headers={
        'Referer': f'http://{user.domain}?param=value',
        'X-Forwarded-For': '1.1.1.1',
    })
    assert response.status == 200
    visits = await Visit.query.gino.all()
    assert len(visits) == 1
    assert str(visits[0].ip) == '1.1.1.1'


async def test_visits_list(client, user, login):
    ua = UserAgent()
    now = datetime(2018, 2, 23)
    yesterday = datetime(2018, 2, 22)
    v2 = await Visit.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4(),
        ip=IPv4Address('172.19.0.1'),
        user_agent=ua.random,
    )
    v1 = await Visit.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4(),
        ip=IPv4Address('127.0.0.1'),
        user_agent=ua.random,
    )
    await login(user)
    response = await client.get('/api/visits/', params={
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
