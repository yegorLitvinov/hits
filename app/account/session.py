from uuid import uuid4

from app.account.models import User
from app.conf import settings
from app.connections.redis import get_redis_pool
from app.core.models import DoesNotExist


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
        user_id = int(user_id)
    except ValueError:
        return
    try:
        user = await User.get(id=user_id, is_active=True)
    except DoesNotExist:
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
