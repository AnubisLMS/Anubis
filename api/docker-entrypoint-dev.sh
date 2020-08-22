#!/bin/sh

set -ex

echo 'Waiting for db...'
until mysqladmin ping -h "${DB_HOST}"; do
    sleep 1
done
echo 'db ready'

if ! [ "${DISABLE_ELK}" = "1" ]; then
    echo 'Waiting for elasticsearch...'
    until curl -q http://elasticsearch:9200/; do
        sleep 1
    done
    echo 'Elasticsearch ready'
fi

echo 'Waiting a second'
sleep 1

echo 'Starting juypter'
jupyter notebook --port 5003 --ip 0.0.0.0
