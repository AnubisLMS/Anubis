LINT_DIRECTORIES := \
	anubis \
	tests \
	migrations
LINT_FILES := $(shell find $(LINT_DIRECTORIES) -name '*.py' | xargs)

COMMIT := $(shell git rev-parse HEAD)

SEED_FILE ?= .data/seed.sql

PYTHON3 ?= $(shell which python3)

help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: run                 # Run dev.py in MINDEBUG mode
run: venv
	env MINDEBUG=1 DEBUG=1 MIGRATE=1 ./venv/bin/python3 dev.py

.PHONY: venv                # Create virtualenv
venv:
	@if [ ! -d venv ]; then \
		python3 -m venv venv; \
		./venv/bin/pip install -r ./requirements/dev.txt; \
	fi

.PHONY: test                # Run tests
test: venv
	./tests/test.sh

.PHONY: coverage            # Run tests and generate a coverage report
coverage:
	env COVERAGE=1 ./tests/test.sh
	./venv/bin/coverage report -m

.PHONY: migrations          # Run alembic migrations
migrations: venv
	./venv/bin/alembic upgrade head

.PHONY: lint                # Run black on lint directories
lint: venv
	@echo 'black to stylize'
	./venv/bin/black $(LINT_FILES)

.PHONY: clean               # Clean directories
clean:
	rm -rf $$(find -name __pycache__) venv .data

$(SEED_FILE): venv
	@echo 'GENERATING SEED'
	env DB_HOST=127.0.0.1 DEBUG=1 \
		venv/bin/python3 -c "import anubis.utils.testing.seed; anubis.utils.testing.seed.seed()"
	@echo 'DUMPING DB TO SEED FILE'
	@mkdir -p .data
	mysqldump -u anubis --password=anubis -h 127.0.0.1 anubis > $(SEED_FILE)

.PHONY: gen-seed            # Generate seed data
gen-seed: $(SEED_FILE) venv

.PHONY: rev-seed            # Revert database using generated seed-data
rev-seed:
	@if [ ! -f $(SEED_FILE) ]; then \
		make $(SEED_FILE); \
	fi
	@echo 'RESETTING DEBUG DB'
	@make -C .. yeetdb
	@echo 'WAITING FOR DB TO START'
	@until mysqladmin -h 127.0.0.1 ping &> /dev/null; do sleep 1; done
	@echo 'REVERTING TO LATEST SEED'
	mysql -u anubis --password=anubis -h 127.0.0.1 anubis < $(SEED_FILE)

.PHONY: autograde-timings   # Run autograde timings test
autograde-timings: venv
	env DB_HOST=127.0.0.1 DEBUG=1 \
		venv/bin/python3 -c "import anubis.utils.testing.autograde_timings; anubis.utils.testing.autograde_timings.main()"

.PHONY: requirements        # pip-compile requirements
requirements: venv
	pip-compile --quiet --upgrade requirements/common.in
	pip-compile --quiet --upgrade requirements/dev.in

debug:
	make -C .. debug
yeetdb:
	make -C .. yeetdb
