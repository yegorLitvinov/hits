from datetime import datetime

import pytz
from sqlalchemy_utils import UUIDType

from app.connections.db import db, get_db_pool
from app.core.models import FilterMixin, SaveMixin


async def increment_counter(user, cookie, path):
    tz = pytz.timezone(user.timezone)
    now = datetime.now(tz=tz).date()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.fetch(
            'insert into visitor (account_id, cookie, path, date) '
            'values ($1, $2, $3, $4) '
            'on conflict (account_id, cookie, path, date) do '
            'update set hits = visitor.hits + 1 ',
            user.id,
            cookie,
            path,
            now,
        )


class Visitor(FilterMixin, SaveMixin):
    table_name = 'visitor'


class GinoVisitor(db.Model):
    __tablename__ = 'visitor'

    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.Integer())
    date = db.Column(db.Date())
    path = db.Column(db.Unicode(1000))
    cookie = db.Column(UUIDType())
    hits = db.Column(db.Integer())

    def __str__(self):
        return f'{self.id}: {self.hits} hits on {self.path} page ({self.date})'

    def to_dict(self):
        d = super().to_dict()
        d['cookie'] = str(d.pop('cookie'))
        d['date'] = d.pop('date').isoformat()
        return d
