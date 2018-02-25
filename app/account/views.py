from sanic.response import json

from app.conf import settings
from app.models import DoesNotExist

from . import session
from .models import User, encrypt_password


def auth_required(coroutine):
    async def inner(request):
        user = await session.get_user(request)
        if not user:
            return json({}, 401)
        # TODO: Figure out how to append user to request
        return await coroutine(request)
    return inner


async def login(request):
    email = request.json.get('email')
    password = request.json.get('password')
    if not (email and password):
        return json({}, 400)
    try:
        user = await User.get(
            is_active=True,
            email=email,
            password=encrypt_password(password),
        )
    except DoesNotExist:
        return json({}, 404)

    response = json({})
    if not request.cookies.get(settings.SESSION_COOKIE_NAME):
        await session.set_user(user, response)

    return response


@auth_required
async def check_auth(request):
    return json({})


@auth_required
async def logout(request):
    response = json({}, 204)
    await session.delete_user(request, response)
    return response
