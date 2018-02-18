import asyncio
from uuid import UUID, uuid4

from sanic.response import text
from sanic.views import HTTPMethodView

from .account import User
from .conf import settings
from .db import DoesNotExist
from .visitor import increment_counter


class VisitView(HTTPMethodView):
    @staticmethod
    def _process_cookie(request, response):
        cookie = request.cookies.get(settings.COOKIE_NAME, '')
        try:
            cookie = str(UUID(cookie))
        except ValueError:
            cookie = str(uuid4())
            response.cookies[settings.COOKIE_NAME] = cookie
            response.cookies[settings.COOKIE_NAME]['max-age'] = settings.COOKIE_MAX_AGE
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


def add_routes(app):
    app.add_route(VisitView.as_view(), '/visit/<api_key>')
