import asyncio

import asyncpg

from .settings import DSN_KWARGS

_pool = None


async def get_pool(loop=None):
    global _pool
    if _pool is None or loop:
        dsn_kwargs = DSN_KWARGS.copy()
        dsn_kwargs['database'] = dsn_kwargs.pop('dbname')
        _pool = await asyncpg.create_pool(
            **dsn_kwargs,
            loop=loop if loop else asyncio.get_event_loop(),
            min_size=2,
            max_size=10
        )
    return _pool


class User:
    def __init__(self, email, domain, is_active, is_superuser, id=None):
        self.id = id
        self.email = email
        self.domain = domain
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.password = None

    @staticmethod
    async def exists(email, password):
        "Check if user exists and return id or None."
        pool = await get_pool()
        async with pool.acquire() as conn:
            password_hash = User.encrypt_password(password)
            id = await conn.fetchval(
                'select id from account where email = $1 and password = $2',
                email,
                password_hash,
            )
        return id

    @staticmethod
    def encrypt_password(password):
        return password

    def set_password(self, password):
        self.password = User.encrypt_password(password)

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
                await conn.execute(
                    'insert into account '
                    '(email, domain, is_active, is_superuser, password) '
                    'values ($1, $2, $3, $4, $5)',
                    self.email,
                    self.domain,
                    self.is_active,
                    self.is_superuser,
                    self.password,
                )
                self.id = await conn.fetchval(
                    'SELECT currval(pg_get_serial_sequence(\'account\', \'id\'));'
                )
        finally:
            await pool.release(conn)
