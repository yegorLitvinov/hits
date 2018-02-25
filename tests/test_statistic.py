from uuid import uuid4
from datetime import date

from app.statistic.models import hits, visits, paths, get_start_end_dates
from app.visitor.models import Visitor

from .conftest import prepare


async def test_hits(db, loop, user, admin):
    await prepare(loop, user, admin)
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    v1 = Visitor(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=uuid4()
    )
    v2 = Visitor(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=uuid4()
    )
    v3 = Visitor(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=uuid4()
    )
    v4 = Visitor(
        account_id=admin.id,
        path='/three',
        date=now,
        cookie=uuid4()
    )
    for v in v1, v2, v3, v4:
        await v.save()
    # user
    hits_count = await hits(user.id, *get_start_end_dates(now, 'day'))
    assert hits_count == 2
    hits_count = await hits(user.id, *get_start_end_dates(now, 'month'))
    assert hits_count == 3
    # admin
    hits_count = await hits(admin.id, *get_start_end_dates(now, 'day'))
    assert hits_count == 1
    hits_count = await hits(admin.id, *get_start_end_dates(now, 'month'))
    assert hits_count == 1


async def test_visits(db, loop, user, admin):
    await prepare(loop, user, admin)
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    cookie1 = uuid4()
    cookie2 = uuid4()
    v1 = Visitor(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=cookie2,
    )
    v2 = Visitor(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=cookie1,
    )
    v3 = Visitor(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=cookie1,
    )
    v4 = Visitor(
        account_id=admin.id,
        path='/three',
        date=now,
        cookie=cookie1,
    )
    v5 = Visitor(
        account_id=admin.id,
        path='/one',
        date=now,
        cookie=cookie2,
    )
    for v in v1, v2, v3, v4, v5:
        await v.save()
    # user
    visits_count = await visits(user.id, *get_start_end_dates(now, 'day'))
    assert visits_count == 1
    visits_count = await visits(user.id, *get_start_end_dates(now, 'month'))
    assert visits_count == 2
    # admin
    visits_count = await visits(admin.id, *get_start_end_dates(now, 'day'))
    assert visits_count == 2
    visits_count = await visits(admin.id, *get_start_end_dates(now, 'month'))
    assert visits_count == 2


async def test_paths(db, loop, user, admin):
    await prepare(loop, user, admin)
    now = date(2018, 2, 23)
    yesterday = date(2018, 2, 22)
    cookie1 = uuid4()
    cookie2 = uuid4()
    v1 = Visitor(
        account_id=user.id,
        path='/one',
        date=yesterday,
        cookie=cookie2,
    )
    v2 = Visitor(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=cookie1,
    )
    v3 = Visitor(
        account_id=user.id,
        path='/one',
        date=now,
        cookie=cookie2,
    )
    v4 = Visitor(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=cookie1,
    )
    v5 = Visitor(
        account_id=user.id,
        path='/two',
        date=now,
        cookie=cookie2,
    )
    v6 = Visitor(
        account_id=user.id,
        path='/three',
        date=yesterday,
        cookie=cookie1,
    )
    for v in v1, v2, v3, v4, v5, v6:
        await v.save()
    paths_stat = await paths(user.id, *get_start_end_dates(now, 'day'))
    assert paths_stat == [
        dict(path='/one', _sum=2),
        dict(path='/two', _sum=2),
    ]
    paths_stat = await paths(user.id, *get_start_end_dates(now, 'month'))
    assert paths_stat == [
        dict(path='/one', _sum=3),
        dict(path='/two', _sum=2),
        dict(path='/three', _sum=1),
    ]
