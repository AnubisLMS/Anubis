DB_HOST := $(shell if nslookup db &> /dev/null; then echo db; else echo 127.0.0.1; fi)

ifndef GUNICORN_OPTIONS
GUNICORN_OPTIONS := ''
endif

ifndef GUNICORN_WORKERS
GUNICORN_WORKERS := 1
endif

.PHONY: all
all: debug


.PHONY: deploy
deploy: db
	python3 db.py
	gunicorn -b 0.0.0.0:5000 -w $(GUNICORN_WORKERS) $(GUNICORN_OPTIONS) src:app

docker-debug: db
	python3 db.py
	python3 dev.py


.PHONY: debug
debug: db venv dev.py
	DB_HOST=$(DB_HOST) ./venv/bin/python db.py
	DB_HOST=$(DB_HOST) DEBUG=1 ./venv/bin/python dev.py


venv:
	virtualenv -p `which python3` venv
	./venv/bin/pip install -r ./requirements.txt


.PHONY: clean
clean:
	rm -rf $$(find -name __pycache__) venv


.PHONY: db
db:
	@echo 'waiting for database to start'
	until mysqladmin ping -u root -h $(DB_HOST) --password=password --silent; do sleep 1; done
	sleep 1
	@echo 'database started'


.PHONY: db-cli
db-cli:
	mysql -u root -h 127.0.0.1 --password=password os
