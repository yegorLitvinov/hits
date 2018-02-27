DSN_KWARGS = dict(
    database='metric',
    user='metric',
    password='password',
    host='localhost',
    port=5432
)

REDIS_ADDR = 'redis://localhost/1'

VISITOR_COOKIE_NAME = '_visitor'
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 2
SESSION_COOKIE_NAME = '_session'
SESSION_COOKIE_MAX_AGE = 60 * 60 * 12

DEBUG = False
WORKERS = 1
