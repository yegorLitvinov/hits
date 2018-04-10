import asyncio

import pytz
import wtforms
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from wtforms import validators

from app.conf import settings

from . import session
from .models import User

blueprint = Blueprint('account', url_prefix='/api/account')


def auth_required(coroutine):
    async def inner(*args):
        request = None
        for arg in args:
            if type(arg) == Request:
                request = arg
        assert request is not None
        user = await session.get_user(request)
        if not user:
            return json({}, 401)
        request['user'] = user
        return await coroutine(*args)
    return inner


class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[validators.input_required()])
    password = wtforms.StringField(validators=[validators.input_required()])


@blueprint.route('/login/', methods=['POST'])
async def login(request):
    form = LoginForm.from_json(request.json)
    if not form.validate():
        return json(form.errors, 400)

    async def not_found():
        if not settings.DEBUG:
            await asyncio.sleep(1)
        return json({}, 404)
    user = await (
        User.query
        .where(User.is_active.is_(True))
        .where(User.email == form.email.data)
        .gino.first()
    )
    if user is None:
        return await not_found()
    if not user.verify_password(form.password.data):
        return await not_found()

    response = json(user.to_dict(), 200)
    if request.cookies.get(settings.SESSION_COOKIE_NAME):
        await session.delete_user(request, response)
    await session.set_user(user, response)

    return response


@blueprint.route('/check-auth/', methods=['POST'])
@auth_required
async def check_auth(request):
    return json({})


@blueprint.route('/logout/', methods=['POST'])
@auth_required
async def logout(request):
    response = json({}, 204)
    await session.delete_user(request, response)
    return response


class ProfileForm(wtforms.Form):
    timezone = wtforms.SelectField(
        choices=list(zip(pytz.all_timezones, pytz.all_timezones))
    )


@blueprint.route('/profile/', methods=['PATCH'])
@auth_required
async def profile(request):
    form = ProfileForm.from_json(request.json)
    if not form.validate():
        return json(form.errors, 400)
    user = request['user']
    await user.update(**form.data).apply()
    return json(user.to_dict(), 200)
