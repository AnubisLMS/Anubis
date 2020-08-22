.PHONY: all
all: venv

venv:
	virtualenv -p `which python3` venv
	./venv/bin/pip install -r ./requirements.txt


.PHONY: clean
clean:
	rm -rf $$(find -name __pycache__) venv

.PHONY: db-cli
db-cli:
	mysql -u anubis -h 127.0.0.1 --password=anubis anubis
