from datetime import date
from uuid import uuid4

import pytest

from app.visitor.models import Visitor

pytestmark = pytest.mark.asyncio


async def test_statistic_unauthenticated(db, client):
    response = await client.get('/api/statistic/')
    assert response.status == 401


async def test_no_params(user, login, client):
    await login(user)
    response = await client.get('/api/statistic/')
    assert response.status == 400
    data = await response.json()
    assert data == {
        'filter_by': ['Not a valid choice'],
        'date': ['This field is required.'],
    }


async def test_invalid_choice(user, login, client):
    await login(user)
    response = await client.get('/api/statistic/', params={
        'filter_by': 'week',
        'date': '22-03-2018',
    })
    assert response.status == 400
    data = await response.json()
    assert data == {
        'filter_by': ['Not a valid choice'],
        'date': ['This field is required.'],
    }


async def test_statistic_success(user, login, client):
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    v1 = Visitor(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4(),
        hits=2,
    )
    v2 = Visitor(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4(),
    )
    for v in v1, v2:
        await v.save()
    await login(user)
    response = await client.get('/api/statistic/', params={
        'filter_by': 'month',
        'date': now.strftime('%Y-%m-%d'),
    })
    assert response.status == 200
    data = await response.json()
    assert data == {
        'hits': 3,
        'visits': 2,
        'new_visits': 2,
        'paths': [
            {'path': '/one', '_sum': 3}
        ]
    }
