from typing import Tuple
from calendar import monthrange
from datetime import datetime, date, time


def get_start_end_dates(now: date, filter_by: str) -> Tuple[datetime, datetime]:
    if filter_by == 'day':
        start_date = datetime.combine(now, time(0, 0))
        end_date = datetime.combine(now, time(23, 59, 59))
    elif filter_by == 'month':
        end_day = monthrange(now.year, now.month)[1]
        start_date = datetime(now.year, now.month, 1)
        end_date = datetime(now.year, now.month, end_day, 23, 59, 59)
    elif filter_by == 'year':
        start_date = datetime(now.year, 1, 1)
        end_date = datetime(now.year, 12, 31, 23, 59, 59)
    else:
        raise Exception(f'Invalid filter_by param: {filter_by}')
    return start_date, end_date
