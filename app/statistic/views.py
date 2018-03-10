import asyncio
from datetime import datetime

import pytz
import wtforms
from sanic import Blueprint
from sanic.response import json

from app.account.views import auth_required

from .models import get_start_end_dates, hits, paths, visits

blueprint = Blueprint('statistic', url_prefix='/api/statistic')


class StatisticForm(wtforms.Form):
    filter_by = wtforms.SelectField(
        choices=(('day', 'Day'), ('month', 'Month'), ('year', 'Year')),
    )


@blueprint.route('/', methods=['GET'])
@auth_required
async def statistic(request):
    form = StatisticForm(request.args)
    if not form.validate():
        return json(form.errors, 400)

    user = request['user']
    tz = pytz.timezone(user.timezone)
    now = datetime.now(tz=tz)
    start_date_str, end_date_str = get_start_end_dates(
        now,
        form.filter_by.data
    )
    tasks = [
        hits(user.id, start_date_str, end_date_str),
        visits(user.id, start_date_str, end_date_str),
        paths(user.id, start_date_str, end_date_str),
    ]
    results = await asyncio.gather(*tasks)
    data = dict(results)
    return json(data)
