#!/bin/bash

tar xzf $1
docker-compose kill elasticsearch
rm -rf /var/lib/docker/volumes/anubis_el_data/_data/nodes
mv usr/share/elasticsearch/data/nodes /var/lib/docker/volumes/anubis_el_data/_data/
rm -rf usr
docker-compose restart elasticsearch 
