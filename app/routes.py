from .account.views import check_auth, login, logout
from .statistic.views import statistic
from .visitor.views import VisitView


def add_routes(app):
    app.add_route(VisitView.as_view(), '/visit/<api_key>')
    app.add_route(login, '/login/', methods=['POST'])
    app.add_route(check_auth, '/check-auth/', methods=['POST'])
    app.add_route(logout, '/logout/', methods=['POST'])
    app.add_route(statistic, '/statistic/', methods=['GET'])
