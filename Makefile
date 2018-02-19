.PHONY: backup
HOST=root@195.201.27.44
PROJECT_SRC=/home/metric
DST=$(realpath ./)

run:
	python develop.py

drop-db:
	psql -c 'drop database metric;'

create-db:
	psql < sql/init.sql

migrate:
	psql -d metric < sql/schema.sql

reset-db: drop-db create-db migrate

isort:
	@isort -rc app

flake:
	@flake8 app test

precommit: isort flake

cleanup:
	find . -name \*.pyc | xargs rm -fv
	find . -name \*.pyo | xargs rm -fv
	find . -name __pycache__ | xargs rm -rfv
	find . -name .mypy_cache | xargs rm -rfv
	find . -name .pytest_cache | xargs rm -rfv

create-requirements:
	pipenv lock -r > requirements/prod.txt
	pipenv lock -rd > requirements/dev.txt
	sort requirements/prod.txt -o requirements/prod.txt
	sort requirements/dev.txt -o requirements/dev.txt

backup:
	mkdir -p backup/db
	rsync -r -e ssh $(HOST):$(PROJECT_SRC)/pgdata $(DST)/backup/db/
