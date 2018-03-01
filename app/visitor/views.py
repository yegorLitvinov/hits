import asyncio
from urllib.parse import urlparse
from uuid import UUID, uuid4

from sanic.response import text
from sanic.views import HTTPMethodView

from app.account.models import User
from app.conf import settings
from app.models import DoesNotExist

from .models import increment_counter


class VisitView(HTTPMethodView):
    @staticmethod
    def _process_cookie(request, response):
        cookie = request.cookies.get(settings.VISITOR_COOKIE_NAME, '')
        try:
            cookie = str(UUID(cookie))
        except ValueError:
            cookie = str(uuid4())
            response.cookies[settings.VISITOR_COOKIE_NAME] = cookie
            response.cookies[settings.VISITOR_COOKIE_NAME]['max-age'] = \
                settings.VISITOR_COOKIE_MAX_AGE
        return cookie

    @staticmethod
    async def _get_user(domain, api_key):
        try:
            return await User.get(domain=domain, api_key=api_key, is_active=True)
        except (DoesNotExist, ValueError) as error:
            if not settings.DEBUG:
                await asyncio.sleep(1)  # bruteforce protection :)

    async def get(self, request, api_key):
        referer = request.headers.get('Referer')
        if not referer:
            return text('Empty referer', 400)
        parse_result = urlparse(referer)
        if not parse_result.netloc:
            return text('Referer\'s domain is empty', status=400)
        user = await VisitView._get_user(parse_result.netloc, api_key)
        if not user:
            return text('Account not found', status=404)

        response = text('')
        cookie = VisitView._process_cookie(request, response)
        await increment_counter(user.id, cookie, parse_result.path or '/')
        return response
