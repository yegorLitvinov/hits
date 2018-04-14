import asyncio
from datetime import datetime
from urllib.parse import urlparse
from uuid import UUID, uuid4

import pytz
from sanic.response import json, text
from sanic.views import HTTPMethodView
from user_agents import parse

from app.account.models import User
from app.account.views import auth_required
from app.conf import settings
from app.connections.db import db
from app.core.utils import get_start_end_dates

from .forms import VisitFilterForm
from .models import Visit
from .utils import serialize_user_agent


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
            UUID(api_key)
        except ValueError:
            user = None
        else:
            user = await (
                User.query
                .where(User.domain == domain)
                .where(User.api_key == api_key)
                .where(User.is_active.is_(True))
                .gino.first()
            )
        if user is None and not settings.DEBUG:
            await asyncio.sleep(1)  # bruteforce protection :)
        return user

    async def get(self, request, api_key):
        referer = request.headers.get('Referer')
        ua_str = request.headers.get('User-Agent', '')
        ip = request.headers.get('X-Forwarded-For')
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
        tz = pytz.timezone(user.timezone)
        now = datetime.now(tz=tz)
        await Visit.create(
            account_id=user.id,
            cookie=cookie,
            path='/' if parse_result.path == '' else parse_result.path,
            date=now,
            ip=ip,
            user_agent=serialize_user_agent(parse(ua_str)),
        )
        return response


class VisitListView(HTTPMethodView):
    @auth_required
    async def get(self, request):
        form = VisitFilterForm(request.args)
        if not form.validate():
            return json(form.errors, 400)

        user = request['user']
        start_date, end_date = get_start_end_dates(
            form.date.data,
            form.filter_by.data
        )
        query = (
            Visit.query
            .where(Visit.date >= start_date)
            .where(Visit.date <= end_date)
            .where(Visit.account_id == user.id)
        )
        visits = await (
            query
            .offset(form.offset.data * form.limit.data)
            .limit(form.limit.data)
            .order_by(form.order_by.data)
            .gino.all()
        )
        total = await db.alias(query, 'cnt').count().gino.scalar()
        return json(
            {
                'data': (v.to_dict() for v in visits),
                'total': total,
            },
            status=200,
        )
