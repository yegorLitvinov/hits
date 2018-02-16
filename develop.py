from aoiklivereload import LiveReloader

from src.app import app

reloader = LiveReloader()
reloader.start_watcher_thread()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
