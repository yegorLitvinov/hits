from app.conf import settings
from app.routes import add_routes
from app import app

if __name__ == '__main__':
    if settings.DEBUG:
        from aoiklivereload import LiveReloader
        reloader = LiveReloader()
        reloader.start_watcher_thread()

    add_routes(app)
    app.run(
        host='0.0.0.0',
        port=8181,
        workers=settings.WORKERS,
        debug=settings.DEBUG
    )
