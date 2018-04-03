import asyncpg
from gino.ext.sanic import Gino
from sqlalchemy.engine.url import URL

from app.conf import settings

_pool = None
db = Gino()


async def get_db_pool():
    global _pool
    if not _pool:
        _pool = await asyncpg.create_pool(
            **settings.DSN_KWARGS,
            min_size=2,
            max_size=10
        )
    return _pool


async def get_db():
    global db
    if db.bind is None:
        kwargs = settings.DSN_KWARGS.copy()
        kwargs['username'] = kwargs.pop('user')
        url = URL('postgresql', **kwargs)
        await db.set_bind(url)
    return db
