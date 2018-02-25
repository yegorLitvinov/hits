import aioredis

from app.conf import settings

_pool = None


async def get_redis_pool(loop=None):
    global _pool
    if not _pool or loop:
        _pool = await aioredis.create_pool(
            settings.REDIS_ADDR,
            loop=loop,
        )
    return _pool
