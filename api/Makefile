LINT_DIRECTORIES := \
	anubis \
	tests \
	migrations

LINT_FILES := $(shell find $(LINT_DIRECTORIES) -name '*.py' | xargs)

.PHONY: all
all: venv

run: venv
	env MINDEBUG=1 DEBUG=1 ./venv/bin/python3 dev.py

venv:
	virtualenv -p `which python3` venv
	./venv/bin/pip install -r ./requirements/dev.txt

debug:
	make -C .. debug

yeetdb:
	make -C .. yeetdb

cleanyeetdb:
	make -C .. cleanyeetdb

test: venv
	./tests/test.sh

.PHONY: migrations       # Run alembic migrations
migrations: venv
	./venv/bin/alembic upgrade head

.PHONY: lint             # Run black on lint directories
lint: venv
	@echo 'black to stylize'
	./venv/bin/black $(LINT_FILES)

.PHONY: clean
clean:
	rm -rf $$(find -name __pycache__) venv .data

.PHONY: pydoc
pydoc: venv
	for i in $(find anubis -name '*.py'); do \
		if [ "$(basename $i)" = "__init__.py" ]; then \
			dirname $i; \
		else \
			echo $i; \
		fi; \
	done \
		| sed 's/\//./g; s/.py$//' \
		| sort \
		| xargs ./venv/bin/python -m pydoc -w

autograde-timings: venv
	env DB_HOST=127.0.0.1 DEBUG=1 \
		venv/bin/python3 -c "import anubis.utils.testing.autograde_timings; anubis.utils.testing.autograde_timings.main()"

.PHONY: requirements
requirements: venv
	pip-compile --quiet requirements/common.in
	pip-compile --quiet requirements/dev.in
