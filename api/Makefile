LINT_DIRECTORIES := \
	anubis \
	tests \
	migrations

LINT_FILES := $(shell find $(LINT_DIRECTORIES) -name '*.py' | xargs)

.PHONY: all
all: venv

venv:
	virtualenv -p `which python3` venv
	./venv/bin/pip install -r ./requirements.txt
	./venv/bin/pip install -U black pytest

debug:
	make -C .. debug

yeetdb:
	make -C .. yeetdb

cleanyeetdb:
	make -C .. cleanyeetdb

.PHONY: migrations       # Run alembic migrations
migrations: venv
	./venv/bin/alembic upgrade head

.PHONY: lint             # Run black on lint directories
lint: venv
	@echo 'black to stylize'
	./venv/bin/black $(LINT_FILES)

.PHONY: clean
clean:
	rm -rf $$(find -name __pycache__) venv

.PHONY: db-cli
db-cli:
	mysql -u anubis -h 127.0.0.1 --password=anubis anubis
