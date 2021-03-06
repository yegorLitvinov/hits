import asyncio
import random
from datetime import datetime

import pytz
from fake_useragent import UserAgent
from locust import HttpLocust, TaskSet, task

from app.account.models import User, encrypt_password
from app.connections.db import get_db

API_KEY = 'ffdf43e0-465b-41a2-942c-c46f274cd68f'
REFERER = 'testing.example.com'
EMAIL = 'test@example.com'
PASSWORD = 'password'


async def create_user():
    await get_db()
    user = await User.query.where(User.email == EMAIL).gino.first()
    kwargs = dict(
        api_key=API_KEY,
        domain=REFERER,
        email=EMAIL,
        is_active=True,
        is_superuser=False,
        password=encrypt_password(PASSWORD),
    )
    if user:
        await user.update(**kwargs).apply()
    else:
        await User.create(**kwargs)


loop = asyncio.get_event_loop()
loop.run_until_complete(create_user())


class UserTasks(TaskSet):
    def on_start(self):
        self.client.post('/api/account/login/', json={
            'email': EMAIL,
            'password': PASSWORD,
        })

    @task
    def statistic(self):
        filter_by = random.choice(['month', 'day', 'year'])
        self.client.get('/api/statistic/', params={
            'filter_by': filter_by,
            'date': datetime.now().date().isoformat(),
        })

    @task
    def profile(self):
        timezone = random.choice(pytz.all_timezones)
        self.client.patch('/api/account/profile/', json={
            'timezone': timezone,
        })


class WebsiteUser(HttpLocust):
    task_set = UserTasks
    host = 'http://localhost:8181'
    min_wait = 100
    max_wait = 1000


class VisitTasks(TaskSet):
    def on_start(self):
        self.ua = UserAgent()

    @task
    def visit(self):
        path = random.choice([
            '', 'about', 'products', 'products/4454',
            'categories', 'categories/sofa/'
        ])
        self.client.get(f'/api/visit/{API_KEY}/', headers={
            'Referer': f'http://{REFERER}/{path}',
            'User-Agent': self.ua.random,
        })


class WebsiteVisit(HttpLocust):
    task_set = VisitTasks
    host = 'http://localhost:8181'
    min_wait = 100
    max_wait = 500
    parent = WebsiteUser
