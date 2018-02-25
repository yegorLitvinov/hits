from datetime import datetime

from sanic import Blueprint
from sanic.response import json

from app.account.views import auth_required

from .models import get_start_end_dates, hits, paths, visits

blueprint = Blueprint('statistic', url_prefix='/api/statistic')


class StatisticForm:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.errors = {}

    def clean(self):
        filter_by = self.kwargs.get('filter_by')
        cleaned_data = {}

        if not isinstance(filter_by, str):
            filter_by = filter_by[0]
        if not filter_by:
            self.errors['filter_by'] = 'This field may not be blank.'
        elif filter_by not in ['day', 'month', 'year']:
            self.errors['filter_by'] = f'Invalid value {filter_by}.'
        else:
            cleaned_data['filter_by'] = filter_by
        return cleaned_data

    def is_valid(self):
        if not getattr(self, 'cleaned_data', None):
            self.cleaned_data = self.clean()
        return not self.errors


@blueprint.route('/', methods=['GET'])
@auth_required
async def statistic(request):
    if not request.args:
        return json({'non_field_errors': ['Empty body']}, 400)
    form = StatisticForm(**request.args)
    if not form.is_valid():
        return json(form.errors, 400)

    now = datetime.now()
    start_date_str, end_date_str = get_start_end_dates(
        now,
        form.cleaned_data['filter_by']
    )
    return json(dict(
        hits=await hits(request['user'].id, start_date_str, end_date_str),
        visits=await visits(request['user'].id, start_date_str, end_date_str),
        paths=await paths(request['user'].id, start_date_str, end_date_str),
    ))
