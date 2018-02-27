import asyncpg

from app.conf import settings

_pool = None


async def get_db_pool():
    global _pool
    if not _pool:
        _pool = await asyncpg.create_pool(
            **settings.DSN_KWARGS,
            min_size=2,
            max_size=10
        )
    return _pool
