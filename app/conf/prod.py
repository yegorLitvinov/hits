from .base import *  # noqa

DSN_KWARGS['host'] = 'metric_pg'  # noqa
REDIS_KWARGS['host'] = 'metric_redis'  # noqa
REDIS_ADDR = f'redis://{REDIS_KWARGS["host"]}/{REDIS_KWARGS["db"]}'  # noqa
