#!/bin/bash


#
# Usage:
#   ./restore.sh # restores to most recent backup
#   ./restore.sh .backups/1584336628 # restore to specific backup
#

set -e

cd $(dirname $(realpath $0))
cd ..

if (( $# == 0 )); then
    LOC=".backups/$(ls .backups | sort -k 1 -g | tail -n 1)"
else
    LOC="$1"
fi


echo "Restoring from: ${LOC}"

restorees() {
    echo "Restoring elasticsearch (expect 10-15 seconds of downtime)"

    tar xzf es.tar.gz
    docker-compose exec elasticsearch rm -rf /usr/share/elasticsearch/data/nodes
    docker-compose kill elasticsearch
    docker cp \
           usr/share/elasticsearch/data/nodes \
           $(docker-compose ps | grep elasticsearch | awk '{print $1}' | head -n 1):/usr/share/elasticsearch/data/nodes
    rm -rf usr
    docker-compose up -d --force-recreate elasticsearch
}

restoredb() {
    gzip -d db.sql.gz
    docker-compose exec -T db mysql -u root --password=password os < db.sql
    gzip db.sql
}


cd ${LOC}

restorees
restoredb
