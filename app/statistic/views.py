from datetime import datetime

from sanic.response import json

from app.account.views import auth_required

from .models import get_start_end_dates, hits, paths, visits


class StatisticForm:
    def __init__(self, **params):
        self.params = params
        self.errors = {}

    def clean(self):
        filter_by = self.params.get('filter_by')
        if not filter_by:
            self.errors['filter_by'] = 'This field may not be blank.'
        if filter_by not in ['day', 'month', 'year']:
            self.errors['filter_by'] = f'Invalid value {filter_by}.'

    def is_valid(self):
        self.clean()
        return not self.errors


@auth_required
async def statistic(request):
    params = request.json()
    form = StatisticForm(params)
    if not form.is_valid():
        return json(form.errors, 400)

    now = datetime.now()
    start_date_str, end_date_str = get_start_end_dates(now, params['filter_by'])
    return json(dict(
        hits=hits(request.user.id, start_date_str, end_date_str),
        visits=visits(request.user.id, start_date_str, end_date_str),
        paths=paths(request.user.id, start_date_str, end_date_str),
    ))
