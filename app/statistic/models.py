from calendar import monthrange
from datetime import date

from app.connections.db import get_db_pool


async def fetch(query, *args):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        res = await conn.fetch(query, *args)
    return res


def get_start_end_dates(now, filter_by):
    if filter_by == 'day':
        start_date_str = end_date_str = now
    elif filter_by == 'month':
        end_day = monthrange(now.year, now.month)[1]
        start_date_str = date(now.year, now.month, 1)
        end_date_str = date(now.year, now.month, end_day)
    elif filter_by == 'year':
        start_date_str = date(now.year, 1, 1)
        end_date_str = date(now.year, 12, 31)
    else:
        raise Exception(f'Invalid filter_by param: {filter_by}')
    return start_date_str, end_date_str


async def hits(account_id, start_date_str, end_date_str):
    query = """
    select sum(hits) as _sum from visitor
    where account_id = $1 and date >= $2 and date <= $3
    """
    res = await fetch(query, account_id, start_date_str, end_date_str)
    return res[0]['_sum']


async def visits(account_id, start_date_str, end_date_str):
    query = """
    select count(*) as _count from (
        select distinct cookie from visitor
        where account_id = $1 and date >= $2 and date <= $3
    ) as cookies
    """
    res = await fetch(query, account_id, start_date_str, end_date_str)
    return res[0]['_count']


async def paths(account_id, start_date_str, end_date_str):
    # TODO: group by index
    query = """
    select sum(hits) as _sum, path from visitor
    where account_id = $1 and date >= $2 and date <= $3
    group by path
    order by _sum desc
    """
    res = await fetch(query, account_id, start_date_str, end_date_str)
    stat = [dict(r) for r in res]
    return stat
