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
	@isort -rc src

flake:
	@flake8 src test

precommit: isort flake
