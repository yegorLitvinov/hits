import asyncio
import random

import pytz
from locust import HttpLocust, TaskSet, task

from app.account.models import User
from app.core.models import DoesNotExist

API_KEY = 'ffdf43e0-465b-41a2-942c-c46f274cd68f'
REFERER = 'testing.example.com'
EMAIL = 'test@example.com'
PASSWORD = 'password'


async def create_user():
    try:
        user = await User.get(email=EMAIL)
    except DoesNotExist:
        user = User()
    user.api_key = API_KEY
    user.domain = REFERER
    user.email = EMAIL
    user.is_active = True
    user.is_superuser = False
    user.set_password(PASSWORD)
    await user.save()


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


class VisitorTasks(TaskSet):
    @task
    def visit(self):
        path = random.choice([
            '', 'about', 'products', 'products/4454',
            'categories', 'categories/sofa/'
        ])
        self.client.get(f'/api/visit/{API_KEY}/', headers={
            'Referer': f'http://{REFERER}/{path}',
        })


class WebsiteVisitor(HttpLocust):
    task_set = VisitorTasks
    host = 'http://localhost:8181'
    min_wait = 100
    max_wait = 500
    parent = WebsiteUser
