LINT_DIRECTORIES := \
	anubis \
	tests \
	migrations

LINT_FILES := $(shell find $(LINT_DIRECTORIES) -name '*.py' | xargs)

.PHONY: all
all: venv

venv:
	virtualenv -p `which python3.8` venv
	./venv/bin/pip install -r ./requirements.txt -r ./requirements-dev.txt

yeetdb:
	make -C .. yeetdb

cleanyeetdb:
	make -C .. cleanyeetdb

.PHONY: lint             # Run autopep8 then black on lint directories
lint: venv
	@echo 'autopep to check and fix un-python things'
	./venv/bin/autopep8 --in-place --aggressive --aggressive $(LINT_FILES)
	@echo 'black to stylize'
	./venv/bin/black $(LINT_FILES)

.PHONY: clean
clean:
	rm -rf $$(find -name __pycache__) venv

.PHONY: db-cli
db-cli:
	mysql -u anubis -h 127.0.0.1 --password=anubis anubis
