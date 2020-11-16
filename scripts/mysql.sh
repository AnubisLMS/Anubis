#!/bin/sh

kubectl port-forward service/mariadb 3306 -n mariadb &
PID=$!

kill_proxy() {
    kill -9 $PID
}

trap kill_proxy SIGINT

exec mysql -u root --password=anubis -h 127.0.0.1
