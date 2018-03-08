from passlib.hash import pbkdf2_sha512

from app.conf import settings
from app.models import FilterMixin, SaveMixin


def encrypt_password(password):
    rounds = 10 if settings.DEBUG else 100_000
    return pbkdf2_sha512.encrypt(password, rounds=rounds)


class User(FilterMixin, SaveMixin):
    table_name = 'account'

    def set_password(self, password):
        self.password = encrypt_password(password)

    def verify_password(self, password):
        return pbkdf2_sha512.verify(password, self.password)
