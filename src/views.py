import asyncio
from uuid import UUID, uuid4

from sanic.response import text
from sanic.views import HTTPMethodView

from .account import User
from .db import DoesNotExist
from .settings import COOKIE_MAX_AGE, COOKIE_NAME
from .visitor import increment_counter


class VisitView(HTTPMethodView):
    def _process_cookie(self, request, response):
        cookie = request.cookies.get(COOKIE_NAME, '')
        try:
            cookie = str(UUID(cookie))
        except ValueError:
            cookie = str(uuid4())
            response.cookies[COOKIE_NAME] = cookie
            response.cookies[COOKIE_NAME]['max-age'] = COOKIE_MAX_AGE
        return cookie

    async def _get_user(self, request, api_key):
        origin = request.headers.get('Origin')
        if not origin:
            return None
        try:
            return await User.get(domain=origin, api_key=api_key, is_active=True)
        except (DoesNotExist, ValueError) as error:
            await asyncio.sleep(1)  # bruteforce protection :)

    def _get_referer_path(self, request):
        "Return referer path, e.g. /about/ or empty string."
        referer = request.headers.get('Referer', '')
        try:
            schema, url = referer.split('://', 1)
            domain, path = url.split('/', 1)
        except ValueError:
            return ''
        return '/' + path

    async def post(self, request, api_key):
        user = await self._get_user(request, api_key)
        if not user:
            return text('Account not found', status=404)
        response = text('', )
        cookie = self._process_cookie(request, response)
        path = self._get_referer_path(request)
        await increment_counter(user.id, cookie, path)
        return response


def add_routes(app):
    app.add_route(VisitView.as_view(), '/visit/<api_key>', methods=['POST'])
