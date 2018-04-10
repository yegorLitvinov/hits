from sanic import Sanic
import wtforms_json
from app.connections.db import get_db

wtforms_json.init()
app = Sanic()


@app.listener('before_server_start')
async def setup_db(app, loop):
    await get_db()
