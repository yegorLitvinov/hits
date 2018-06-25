import aioredis

from app.conf import settings

_pool = None


async def get_redis_pool():
    global _pool
    if not _pool:
        _pool = await aioredis.create_pool(
            f'{settings.REDIS_ADDR}/{settings.REDIS_DB}'
        )
    return _pool
