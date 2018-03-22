import asyncio

import wtforms
from sanic import Blueprint
from sanic.response import json

from app.account.views import auth_required

from .models import get_start_end_dates, hits, new_visits, paths, visits

blueprint = Blueprint('statistic', url_prefix='/api/statistic')


class StatisticForm(wtforms.Form):
    filter_by = wtforms.SelectField(
        choices=(('day', 'Day'), ('month', 'Month'), ('year', 'Year')),
    )
    date = wtforms.DateField(validators=[wtforms.validators.DataRequired()])


@blueprint.route('/', methods=['GET'])
@auth_required
async def statistic(request):
    form = StatisticForm(request.args)
    if not form.validate():
        return json(form.errors, 400)

    user = request['user']
    start_date, end_date = get_start_end_dates(
        form.date.data,
        form.filter_by.data
    )
    tasks = [
        hits(user.id, start_date, end_date),
        visits(user.id, start_date, end_date),
        new_visits(user.id, start_date, end_date),
        paths(user.id, start_date, end_date),
    ]
    results = await asyncio.gather(*tasks)
    data = dict(results)
    return json(data)
