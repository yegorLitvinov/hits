from .base import *  # noqa

DEBUG = True
DSN_KWARGS['database'] = 'metric_test'  # noqa
REDIS_ADDR = 'redis://localhost'
REDIS_DB = 15
