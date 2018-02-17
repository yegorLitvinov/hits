from aoiklivereload import LiveReloader
from sanic import Sanic

from src.views import add_routes

reloader = LiveReloader()
reloader.start_watcher_thread()

if __name__ == '__main__':
    app = Sanic()
    add_routes(app)
    app.run(host='0.0.0.0', port=8181, debug=True)
