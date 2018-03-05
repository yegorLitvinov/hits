import asyncio
from datetime import datetime

from sanic import Blueprint
from sanic.response import json
from wtforms import Form, SelectField

from app.account.views import auth_required

from .models import get_start_end_dates, hits, paths, visits

blueprint = Blueprint('statistic', url_prefix='/api/statistic')


class StatisticForm(Form):
    filter_by = SelectField(
        choices=(('day', 'Day'), ('month', 'Month'), ('year', 'Year')),
    )


@blueprint.route('/', methods=['GET'])
@auth_required
async def statistic(request):
    form = StatisticForm(request.args)
    if not form.validate():
        return json(form.errors, 400)

    now = datetime.now()
    start_date_str, end_date_str = get_start_end_dates(
        now,
        form.filter_by.data
    )
    tasks = [
        hits(request['user'].id, start_date_str, end_date_str),
        visits(request['user'].id, start_date_str, end_date_str),
        paths(request['user'].id, start_date_str, end_date_str),
    ]
    results = await asyncio.gather(*tasks)
    data = dict(results)
    return json(data)
