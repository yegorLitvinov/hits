from datetime import datetime

import pytz

from app.connections.db import get_db_pool
from app.models import FilterMixin, SaveMixin


async def increment_counter(user, cookie, path):
    tz = pytz.timezone(user.timezone)
    now = datetime.now(tz=tz).date()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.fetch(
            'insert into visitor (account_id, cookie, path, date) '
            'values ($1, $2, $3, $4) '
            'on conflict (account_id, cookie, path, date) do '
            'update set hits = visitor.hits + 1 ',
            user.id,
            cookie,
            path,
            now,
        )


class Visitor(FilterMixin, SaveMixin):
    table_name = 'visitor'
