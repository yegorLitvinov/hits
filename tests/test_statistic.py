from datetime import date
from uuid import uuid4

import pytest

from app.core.utils import get_start_end_dates
from app.statistic.models import hits, new_visits, paths, visits
from app.visitor.models import Visitor

pytestmark = pytest.mark.asyncio


async def test_hits(user, admin):
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4()
    )
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4()
    )
    await Visitor.create(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=uuid4()
    )
    await Visitor.create(
        account_id=admin.id,
        path='/three',
        date=now,
        cookie=uuid4()
    )
    # user
    _, hits_count = await hits(user.id, *get_start_end_dates(now, 'day'))
    assert hits_count == 2
    _, hits_count = await hits(user.id, *get_start_end_dates(now, 'month'))
    assert hits_count == 3
    # admin
    _, hits_count = await hits(admin.id, *get_start_end_dates(now, 'day'))
    assert hits_count == 1
    _, hits_count = await hits(admin.id, *get_start_end_dates(now, 'month'))
    assert hits_count == 1


async def test_visits(user, admin):
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    cookie1 = uuid4()
    cookie2 = uuid4()
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=cookie2,
    )
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=cookie1,
    )
    await Visitor.create(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=cookie1,
    )
    await Visitor.create(
        account_id=admin.id,
        path='/three',
        date=now,
        cookie=cookie1,
    )
    await Visitor.create(
        account_id=admin.id,
        path='/one',
        date=now,
        cookie=cookie2,
    )
    # user
    _, visits_count = await visits(user.id, *get_start_end_dates(now, 'day'))
    assert visits_count == 1
    _, visits_count = await visits(user.id, *get_start_end_dates(now, 'month'))
    assert visits_count == 2
    # admin
    _, visits_count = await visits(admin.id, *get_start_end_dates(now, 'day'))
    assert visits_count == 2
    _, visits_count = await visits(admin.id, *get_start_end_dates(now, 'month'))
    assert visits_count == 2


async def test_new_visits(user):
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    last_month = date(2018, 1, 14)
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4(),
    )
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4(),
    )
    await Visitor.create(
        account_id=user.id,
        path='/two',
        date=last_month,
        cookie=uuid4(),
    )
    _, new_visits_count = await new_visits(user.id, *get_start_end_dates(now, 'day'))
    assert new_visits_count == 1
    _, new_visits_count = await new_visits(user.id, *get_start_end_dates(now, 'month'))
    assert new_visits_count == 2


async def test_paths(user, admin):
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    cookie1 = uuid4()
    cookie2 = uuid4()
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=cookie2,
    )
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=cookie1,
    )
    await Visitor.create(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=cookie2,
    )
    await Visitor.create(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=cookie1,
    )
    await Visitor.create(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=cookie2,
    )
    await Visitor.create(
        account_id=user.id,
        path='/three',
        date=yesterday,
        cookie=cookie1,
    )
    _, paths_stat = await paths(user.id, *get_start_end_dates(now, 'day'))
    assert paths_stat == [
        dict(path='/one', _sum=2),
        dict(path='/two', _sum=2),
    ]
    _, paths_stat = await paths(user.id, *get_start_end_dates(now, 'month'))
    assert paths_stat == [
        dict(path='/one', _sum=3),
        dict(path='/two', _sum=2),
        dict(path='/three', _sum=1),
    ]
