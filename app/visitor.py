from datetime import datetime

from .db import get_db_pool


async def increment_counter(account_id, cookie, path):
    now = datetime.now().date()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.fetch(
            'insert into visitor (account_id, cookie, path, date) '
            'values ($1, $2, $3, $4) '
            'on conflict (account_id, cookie, path, date) do '
            'update set hits = visitor.hits + 1 ',
            account_id,
            cookie,
            path,
            now,
        )
