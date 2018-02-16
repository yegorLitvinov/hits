from sanic.response import text

from .app import app


@app.route('/')
async def index(request):
    return text('Hello, world!')
