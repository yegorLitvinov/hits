# set -e

PYTHONPATH=`pwd` SETTINGS_MODULE=app.conf.prod python3 app/migrations/migrate.py
PYTHONPATH=`pwd` SETTINGS_MODULE=app.conf.prod python3 -m app
