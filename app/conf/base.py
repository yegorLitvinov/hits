DSN_KWARGS = dict(
    database='metric',
    user='metric',
    password='password',
    host='localhost',
    port=5432
)

# app.config.DB_HOST = 'metric'
# app.config.DB_PORT = 5432
# app.config.DB_USER = 'metric'
# app.config.DB_PASSWORD = 'password'
# app.config.DB_DATABASE = 'metric'
# app.config.DB_POOL_MIN_SIZE = 2
# app.config.DB_POOL_MAX_SIZE = 10
# app.config.DB_USE_CONNECTION_FOR_REQUEST = True

REDIS_ADDR = 'redis://localhost/1'

VISITOR_COOKIE_NAME = '_visitor'
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 2
SESSION_COOKIE_NAME = '_session'
SESSION_COOKIE_MAX_AGE = 60 * 60 * 12

DEBUG = False
WORKERS = 1
