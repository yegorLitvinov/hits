import asyncio
from uuid import UUID, uuid4

from sanic.response import json, text
from sanic.views import HTTPMethodView

from . import session
from .account import User, encrypt_password
from .conf import settings
from .db import DoesNotExist
from .visitor import increment_counter


def auth_required(coroutine):
    async def inner(request):
        user = await session.get_user(request)
        if not user:
            return json({}, 401)
        return await coroutine(request)
    return inner


class VisitView(HTTPMethodView):
    @staticmethod
    def _process_cookie(request, response):
        cookie = request.cookies.get(settings.VISITOR_COOKIE_NAME, '')
        try:
            cookie = str(UUID(cookie))
        except ValueError:
            cookie = str(uuid4())
            response.cookies[settings.VISITOR_COOKIE_NAME] = cookie
            response.cookies[settings.VISITOR_COOKIE_NAME]['max-age'] = settings.VISITOR_COOKIE_MAX_AGE
        return cookie

    @staticmethod
    async def _get_user(domain, api_key):
        try:
            return await User.get(domain=domain, api_key=api_key, is_active=True)
        except (DoesNotExist, ValueError) as error:
            if not settings.DEBUG:
                await asyncio.sleep(1)  # bruteforce protection :)

    @staticmethod
    def _parse_referer(request):
        "Return (domain, path)."
        referer = request.headers.get('Referer', '')
        try:
            schema, url = referer.split('://', 1)
            domain, path = url.split('/', 1)
        except ValueError:
            return '', ''
        return domain, '/' + path

    async def get(self, request, api_key):
        domain, path = VisitView._parse_referer(request)
        print(domain, path)
        if not domain:
            return text('Referer\'s domain is empty', status=400)
        user = await VisitView._get_user(domain, api_key)
        if not user:
            return text('Account not found', status=404)

        response = text('')
        cookie = VisitView._process_cookie(request, response)
        await increment_counter(user.id, cookie, path)
        return response


async def login(request):
    email = request.json.get('email')
    password = request.json.get('password')
    if not (email and password):
        return json({}, 400)
    try:
        user = await User.get(email=email, password=encrypt_password(password))
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


def add_routes(app):
    app.add_route(VisitView.as_view(), '/visit/<api_key>')
    app.add_route(login, '/login/', methods=['POST'])
    app.add_route(check_auth, '/check-auth/', methods=['POST'])
    app.add_route(logout, '/logout/', methods=['POST'])
