from datetime import datetime
from uuid import uuid4

import pytest

from app.visit.models import Visit

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
    now = datetime(2018, 2, 23)
    yesterday = datetime(2018, 2, 22)
    await Visit.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4(),
    )
    await Visit.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4(),
    )
    await login(user)
    response = await client.get('/api/statistic/', params={
        'filter_by': 'month',
        'date': now.strftime('%Y-%m-%d'),
    })
    assert response.status == 200
    data = await response.json()
    assert data == {
        'hits': 2,
        'visits': 2,
        'new_visits': 2,
        'paths': [
            {'path': '/one', '_sum': 2}
        ]
    }
