import asyncpg

from app.conf import settings

_pool = None


async def get_db_pool(loop=None):
    global _pool
    if not _pool or loop:
        dsn_kwargs = settings.DSN_KWARGS.copy()
        dsn_kwargs['database'] = dsn_kwargs.pop('dbname')
        _pool = await asyncpg.create_pool(
            **dsn_kwargs,
            loop=loop,
            min_size=2,
            max_size=10
        )
    return _pool
