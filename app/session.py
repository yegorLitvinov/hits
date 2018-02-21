from uuid import uuid4

import aioredis

from .account import User
from .conf import settings
from .db import DoesNotExist

_pool = None


async def get_redis_pool(loop=None):
    global _pool
    if not _pool or loop:
        _pool = await aioredis.create_pool(
            settings.REDIS_ADDR,
            loop=loop,
        )
    return _pool


async def get_user(request):
    cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not cookie:
        return
    pool = await get_redis_pool()
    async with pool.get() as conn:
        user_id = await conn.execute('get', cookie)
    if not user_id:
        return
    try:
        user = await User.get(id=int(user_id), is_active=True)
    except (DoesNotExist, ValueError):
        return
    return user


async def set_user(user, response):
    cookie = str(uuid4())
    response.cookies[settings.SESSION_COOKIE_NAME] = cookie
    response.cookies[settings.SESSION_COOKIE_NAME]['max-age'] = \
        settings.SESSION_COOKIE_MAX_AGE
    pool = await get_redis_pool()
    async with pool.get() as conn:
        await conn.execute('set', cookie, user.id)
        await conn.execute('expire', cookie, settings.SESSION_COOKIE_MAX_AGE)


async def delete_user(request, response):
    cookie = request.cookies[settings.SESSION_COOKIE_NAME]
    pool = await get_redis_pool()
    async with pool.get() as conn:
        await conn.execute('del', cookie)
    response.cookies[settings.SESSION_COOKIE_NAME] = ''
    response.cookies[settings.SESSION_COOKIE_NAME]['max-age'] = -1
