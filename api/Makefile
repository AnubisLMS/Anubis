all: debug

DB_HOST = $(shell if nslookup db &> /dev/null; then echo db; else echo 127.0.0.1; fi)

deploy: db
	gunicorn -b 0.0.0.0:5000 -w 8 app:app

debug: db venv
	DEBUG=1 DB_HOST=$(DB_HOST) ./venv/bin/python dev.py

venv:
	virtualenv -p `which python3` venv
	./venv/bin/pip install -r ./requirements.txt

db:
	@echo 'waiting for database to start'
	until mysqladmin ping -u root -h $(DB_HOST) --password=password --silent; do sleep 1; done
	sleep 1
	@echo 'database started'

db-cli:
	mysql -u root -h 127.0.0.1 --password=password os
