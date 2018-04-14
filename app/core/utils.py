from calendar import monthrange
from datetime import datetime


def get_start_end_dates(now, filter_by):
    if filter_by == 'day':
        start_date = end_date = now
    elif filter_by == 'month':
        end_day = monthrange(now.year, now.month)[1]
        start_date = datetime(now.year, now.month, 1)
        end_date = datetime(now.year, now.month, end_day)
    elif filter_by == 'year':
        start_date = datetime(now.year, 1, 1)
        end_date = datetime(now.year, 12, 31)
    else:
        raise Exception(f'Invalid filter_by param: {filter_by}')
    return start_date, end_date
