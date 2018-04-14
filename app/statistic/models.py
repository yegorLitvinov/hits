from app.connections.db import get_db_pool


async def fetch(query, *args):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        res = await conn.fetch(query, *args)
    return res


async def hits(account_id, start_date, end_date):
    query = """
    select count(*) as _sum from visit
    where account_id = $1 and date >= $2 and date <= $3
    """
    res = await fetch(query, account_id, start_date, end_date)
    return 'hits', res[0]['_sum']


async def visits(account_id, start_date, end_date):
    query = """
    select count(*) as _count from (
        select distinct cookie from visit
        where account_id = $1 and date >= $2 and date <= $3
    ) as cookies
    """
    res = await fetch(query, account_id, start_date, end_date)
    return 'visits', res[0]['_count']


async def new_visits(account_id, start_date, end_date):
    query = """
    select count(*) as _count from (
        select distinct cookie from visit
        where cookie not in (
            select distinct cookie from visit
            where account_id = $1 and date < $2
        ) and account_id = $1 and date >= $2 and date <= $3
    ) as cookies
    """
    res = await fetch(query, account_id, start_date, end_date)
    return 'new_visits', res[0]['_count']


async def paths(account_id, start_date, end_date):
    # TODO: group by index
    query = """
    select count(*) as _sum, path from visit
    where account_id = $1 and date >= $2 and date <= $3
    group by path
    order by _sum desc
    limit 10
    """
    res = await fetch(query, account_id, start_date, end_date)
    stat = [dict(r) for r in res]
    return 'paths', stat
