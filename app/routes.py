from .account.views import blueprint as account_blueprint
from .statistic.views import blueprint as statistic_blueprint
from .visitor.views import VisitView


def add_routes(app):
    app.blueprint(account_blueprint)
    app.blueprint(statistic_blueprint)
    app.add_route(VisitView.as_view(), '/api/visit/<api_key>')
