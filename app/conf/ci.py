from .dev import *  # noqa

DSN_KWARGS = dict(
    database='metric',
    user='metric',
    password='password',
    host='pg',
    port=5432
)

REDIS_ADDR = 'redis://redis/1'
