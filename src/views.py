from sanic.response import text

from .account import User
from .db import DoesNotExist
from .settings import COOKIE_NAME


async def visit(request, api_key):
    try:
        user = await User.get(domain='', api_key=api_key)
    except (DoesNotExist, ValueError):
        return text('Account not found', status=404)
    cookie = request.cookies.get(COOKIE_NAME)
    return text('')


def add_routes(app):
    app.add_route(visit, '/visit/<api_key>', methods=['POST'])
