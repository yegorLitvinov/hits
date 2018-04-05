import asyncio
from urllib.parse import urlparse
from uuid import UUID, uuid4

from sanic.response import json, text
from sanic.views import HTTPMethodView

from app.account.models import User
from app.account.views import auth_required
from app.conf import settings
from app.connections.db import get_db
from app.core.models import DoesNotExist
from app.core.utils import get_start_end_dates

from .forms import VisitorFilterForm
from .models import GinoVisitor, increment_counter


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
        await increment_counter(user, cookie, parse_result.path or '/')
        return response


class VisitorListView(HTTPMethodView):
    @auth_required
    async def get(self, request):
        form = VisitorFilterForm(request.args)
        if not form.validate():
            return json(form.errors, 400)

        user = request['user']
        start_date, end_date = get_start_end_dates(
            form.date.data,
            form.filter_by.data
        )
        db = await get_db()
        query = (
            GinoVisitor.query
            .where(GinoVisitor.date >= start_date)
            .where(GinoVisitor.date <= end_date)
            .where(GinoVisitor.account_id == user.id)
        )
        visitors = await (
            query
            .offset(form.offset.data * form.limit.data)
            .limit(form.limit.data)
            .order_by(form.order_by.data)
            .gino.all()
        )
        total = await db.alias(query, 'cnt').count().gino.scalar()
        return json(
            {
                'data': (v.to_dict() for v in visitors),
                'total': total,
            },
            status=200,
        )
