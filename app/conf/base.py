DSN_KWARGS = dict(
    dbname='metric',
    user='metric',
    password='password',
    host='localhost',
    port=5432
)

REDIS_KWARGS = dict(
    host='localhost',
    port=6379,
    db=1
)
REDIS_ADDR = f'redis://{REDIS_KWARGS["host"]}/{REDIS_KWARGS["db"]}'

VISITOR_COOKIE_NAME = '_visitor'
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 2
SESSION_COOKIE_NAME = '_session'
SESSION_COOKIE_MAX_AGE = 60 * 60 * 12

DEBUG = False
WORKERS = 2
