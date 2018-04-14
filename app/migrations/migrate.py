import asyncio
import os
from logging import Logger

from asyncpg.exceptions import PostgresError, UndefinedTableError

from app.connections.db import get_db_pool

logger = Logger(__name__)


async def migrate():
    pool = await get_db_pool()
    migrations_dir = os.path.dirname(__file__)
    async with pool.acquire() as conn:
        try:
            applied_migrations = [
                rec['name']
                for rec in await conn.fetch('select name from migration')
            ]
        except UndefinedTableError:
            applied_migrations = []

        for filename in sorted(os.listdir(migrations_dir)):
            if not filename.endswith('.sql'):
                continue
            if filename in applied_migrations:
                continue
            content = open(os.path.join(migrations_dir, filename)).read()
            try:
                await conn.execute(content)
            except PostgresError as error:
                logger.error(str(error))
            await conn.execute(
                'insert into migration (name) values ($1)',
                filename,
            )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrate())
    loop.close()
