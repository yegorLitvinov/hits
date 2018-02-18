import asyncio

import asyncpg

from .conf import settings

_pool = None


async def get_pool(loop=None):
    global _pool
    if _pool is None or loop:
        dsn_kwargs = settings.DSN_KWARGS.copy()
        dsn_kwargs['database'] = dsn_kwargs.pop('dbname')
        _pool = await asyncpg.create_pool(
            **dsn_kwargs,
            loop=loop if loop else asyncio.get_event_loop(),
            min_size=2,
            max_size=10
        )
    return _pool


class DBError(Exception):
    pass


class DoesNotExist(DBError):
    pass


class MultipleObjectsReturned(DBError):
    pass


class FilterMixin:
    table_name = NotImplemented

    @classmethod
    async def filter(cls, **kwargs):
        query = f'select * from {cls.table_name} '
        if kwargs:
            query += 'where ' + ' and '.join(
                [f'{key} = ${num}' for num, key in enumerate(kwargs.keys(), 1)]
            )
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *kwargs.values())
        return [cls(**row) for row in rows]

    @classmethod
    async def get(cls, **kwargs):
        objects = await cls.filter(**kwargs)
        if not objects:
            raise DoesNotExist
        elif len(objects) > 1:
            raise MultipleObjectsReturned
        return objects[0]

    @classmethod
    async def all(cls):
        return await cls.filter()
