from passlib.hash import pbkdf2_sha512

from app.conf import settings
from app.connections.db import db

from sqlalchemy_utils import UUIDType


def encrypt_password(password):
    rounds = 10 if settings.DEBUG else 100_000
    return pbkdf2_sha512.encrypt(password, rounds=rounds)


class User(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer(), primary_key=True)
    api_key = db.Column(UUIDType())
    domain = db.Column(db.Unicode(100))
    email = db.Column(db.Unicode(100))
    is_active = db.Column(db.Boolean())
    is_superuser = db.Column(db.Boolean())
    password = db.Column(db.Unicode(1000))
    timezone = db.Column(db.Unicode(128))

    def __repr__(self):
        return f'User(domain={self.domain}, email={self.email}, api_key={self.api_key})'

    def verify_password(self, password):
        return pbkdf2_sha512.verify(password, self.password)

    def to_dict(self):
        fields = super().to_dict()
        fields.pop('password')
        fields['api_key'] = fields['api_key'].hex
        return fields
