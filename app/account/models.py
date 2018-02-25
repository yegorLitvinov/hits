from app.models import FilterMixin, SaveMixin


def encrypt_password(password):
    # TODO:
    return password


class User(FilterMixin, SaveMixin):
    table_name = 'account'

    def set_password(self, password):
        self.password = encrypt_password(password)
