import asyncio
import os
from logging import Logger

from asyncpg.exceptions import PostgresError

from app.db import get_db_pool

logger = Logger(__name__)


async def migrate():
    pool = await get_db_pool()
    migrations_dir = os.path.dirname(__file__)
    async with pool.acquire() as conn:
        for filename in os.listdir(migrations_dir):
            if not filename.endswith('.sql'):
                continue
            content = open(os.path.join(migrations_dir, filename)).read()
            try:
                await conn.execute(content)
            except PostgresError as error:
                logger.warn(str(error))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrate())
    loop.close()
