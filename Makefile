.PHONY: backup
HOST=root@195.201.27.44
USER=metric
DB=$(USER)
PROJECT_SRC=/home/$(USER)
DST=$(realpath ./)

dev:
	python -m app

dropdb:
	psql -c 'drop database $(DB);'

createdb:
	psql < pg/init.sql

migrate-from-shell:
	for file in `ls app/migrations/*.sql` ; do \
		psql -d $(DB) < $$file ; \
	done

migrate:
	python3 app/migrations/migrate.py

resetdb: dropdb createdb

isort:
	@isort -rc app tests locustfile.py fabfile.py

flake:
	@flake8 app test locustfile.py fabfile.py

precommit: flake isort

cleanup:
	find . -name \*.pyc | xargs rm -fv
	find . -name \*.pyo | xargs rm -fv
	find . -name __pycache__ | xargs rm -rfv
	find . -name .mypy_cache | xargs rm -rfv
	find . -name .pytest_cache | xargs rm -rfv

create-req:
	pipenv lock -r > app/requirements/prod.txt
	pipenv lock -rd > app/requirements/dev.txt
	sort app/requirements/prod.txt -o app/requirements/prod.txt
	sort app/requirements/dev.txt -o app/requirements/dev.txt

backup:
	mkdir -p backup/db
	rsync -r -e ssh $(HOST):$(PROJECT_SRC)/pgdata $(DST)/backup/db/

test-cov:
	py.test --cov=app --cov-config .coveragerc --cov-report html:htmlcov

deploy-app:
	make cleanup
	fab app

deploy-front:
	cd front && yarn && yarn run build
	rm front/dist/static/js/*.map
	@fab copy_front
