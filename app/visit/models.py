from sqlalchemy_utils import IPAddressType, JSONType, UUIDType

from app.connections.db import db


class Visit(db.Model):
    __tablename__ = 'visit'

    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.Integer())  # TODO: foreign key
    date = db.Column(db.DateTime())
    path = db.Column(db.Unicode(1000))
    cookie = db.Column(UUIDType())
    ip = db.Column(IPAddressType())
    user_agent = db.Column(JSONType)

    def __repr__(self):
        return f'Visit #{self.id} on "{self.path}" page at "{self.date}"'

    def to_dict(self):
        d = super().to_dict()
        d['cookie'] = str(d.pop('cookie'))
        d['date'] = d.pop('date').isoformat()
        return d
