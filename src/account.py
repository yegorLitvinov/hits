from uuid import uuid4

from .db import get_pool


def encrypt_password(password):
    return password


class User:
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

    @staticmethod
    async def get_by_credentials(email, password):
        pool = await get_pool()
        async with pool.acquire() as conn:
            password_hash = encrypt_password(password)
            row = await conn.fetchrow(
                'select * from account where email = $1 and password = $2',
                email,
                password_hash,
            )
        if row:
            return User(**row)

    @staticmethod
    async def get_by_id(id):
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'select * from account where id = $1 ',
                id
            )
        if row:
            return User(**row)

    async def save(self):
        pool = await get_pool()
        conn = await pool.acquire()
        try:
            if self.id:
                await conn.execute(
                    'update account '
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
                    'insert into account '
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
                    'SELECT currval(pg_get_serial_sequence(\'account\', \'id\'));'
                )
        finally:
            await pool.release(conn)
