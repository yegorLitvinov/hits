import wtforms
from wtforms.validators import NumberRange

from app.core.forms import StatisticFilterForm


class VisitorFilterForm(StatisticFilterForm):
    offset = wtforms.IntegerField(validators=[NumberRange(min=0)])
    limit = wtforms.IntegerField(validators=[NumberRange(min=1)])
    order_by = wtforms.SelectField(
        choices=(('id', 'Id'), ('cookie', 'Cookie'), ('hits', 'Hits'), ('date', 'Date')),
    )
