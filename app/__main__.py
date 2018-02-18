from sanic import Sanic

from app.conf import settings
from app.views import add_routes

if __name__ == '__main__':
    if settings.DEBUG:
        from aoiklivereload import LiveReloader
        reloader = LiveReloader()
        reloader.start_watcher_thread()

    app = Sanic()
    add_routes(app)
    app.run(
        host='0.0.0.0',
        port=8181,
        workers=settings.WORKERS,
        debug=settings.DEBUG
    )
