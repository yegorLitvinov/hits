import wtforms


class StatisticFilterForm(wtforms.Form):
    filter_by = wtforms.SelectField(
        choices=(('day', 'Day'), ('month', 'Month'), ('year', 'Year')),
    )
    date = wtforms.DateField(validators=[wtforms.validators.DataRequired()])
