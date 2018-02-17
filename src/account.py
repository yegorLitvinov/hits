from uuid import uuid4

from .db import get_pool, FilterMixin


def encrypt_password(password):
    return password


class User(FilterMixin):
    table_name = 'account'

    def __init__(self,
                 email,
                 domain,
                 is_active,
                 is_superuser,
                 id=None,
                 password=None,
                 api_key=None):
        self.id = id
        self.email = email
        self.domain = domain
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.password = password
        self.api_key = api_key

    def set_password(self, password):
        self.password = encrypt_password(password)

    def __eq__(self, other):
        return self.id == other.id

    async def save(self):
        pool = await get_pool()
        conn = await pool.acquire()
        try:
            if self.id:
                await conn.execute(
                    f'update {self.table_name} '
                    'set (email, domain, is_active, is_superuser, password) = '
                    '($1, $2, $3, $4, $5) where id = $6',
                    self.email,
                    self.domain,
                    self.is_active,
                    self.is_superuser,
                    self.password,
                    self.id,
                )
            else:
                self.api_key = uuid4()
                await conn.execute(
                    f'insert into {self.table_name} '
                    '(email, domain, is_active, is_superuser, api_key, password) '
                    'values ($1, $2, $3, $4, $5, $6)',
                    self.email,
                    self.domain,
                    self.is_active,
                    self.is_superuser,
                    self.api_key,
                    self.password,
                )
                self.id = await conn.fetchval(
                    f'SELECT currval(pg_get_serial_sequence(\'{self.table_name}\', \'id\'));'
                )
        finally:
            await pool.release(conn)
