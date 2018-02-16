import asyncio

import asyncpg

from .settings import DSN_KWARGS

_pool = None


async def get_pool(loop=None):
    global _pool
    if _pool is None or loop:
        dsn_kwargs = DSN_KWARGS.copy()
        dsn_kwargs['database'] = dsn_kwargs.pop('dbname')
        _pool = await asyncpg.create_pool(
            **dsn_kwargs,
            loop=loop if loop else asyncio.get_event_loop(),
            min_size=2,
            max_size=10
        )
    return _pool
