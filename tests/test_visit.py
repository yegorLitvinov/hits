from datetime import datetime
from uuid import uuid4

import pytest
from fake_useragent import UserAgent
from user_agents import parse

from app.visit.models import Visit
from app.visit.utils import serialize_user_agent

pytestmark = pytest.mark.asyncio


async def test_serialize_user_agent():
    ua_str = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36'
    )
    assert serialize_user_agent(parse(ua_str)) == {
        'browser': {
            'family': 'Chromium',
            'version': (65, 0, 3325),
            'version_string': '65.0.3325',
        },
        'os': {
            'family': 'Ubuntu',
            'version': (),
            'version_string': '',
        },
        'device': {
            'family': 'Other',
            'brand': None,
            'model': None,
        },
        'is_bot': False,
        'is_email_client': False,
        'is_mobile': False,
        'is_pc': True,
        'is_tablet': False,
        'is_touch_capable': False,
        'ua_string': ua_str,
    }


async def test_save_many_random_user_agents(user):
    ua = UserAgent()
    for i in range(10):
        await Visit.create(
            user_agent=serialize_user_agent(parse(ua.random)),
            account_id=user.id,
            path='/',
            cookie=uuid4(),
            date=datetime.now(),
        )
