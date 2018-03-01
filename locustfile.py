import asyncio
import random

import asyncpg
from locust import HttpLocust, TaskSet, task

from app.conf import settings

API_KEY = 'ffdf43e0-465b-41a2-942c-c46f274cd68f'
REFERER = 'testing.example.com'
EMAIL = 'test@example.com'
PASSWORD = 'password'


async def create_user():
    db_conn = await asyncpg.connect(**settings.DSN_KWARGS)
    await db_conn.fetch(
        """
        insert into account
        (api_key, domain, email, is_active, is_superuser, password)
        values ('{}', '{}', '{}', true, true, '{}')
        on conflict do nothing
        """.format(API_KEY, REFERER, EMAIL, PASSWORD)
    )
    await db_conn.close()


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
        result = self.client.get('/api/statistic/', params={
            'filter_by': 'month',
        })
        print(result)


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
    max_wait = 1000
    parent = WebsiteUser
