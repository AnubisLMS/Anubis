#!/bin/bash

tar xzf $1
docker-compose exec elasticsearch rm -rf /usr/share/elasticsearch/data/nodes
docker-compose kill elasticsearch
docker cp \
       usr/share/elasticsearch/data/nodes \
       $(docker-compose ps | grep elasticsearch | awk '{print $1}' | head -n 1):/usr/share/elasticsearch/data/nodes
rm -rf usr
docker-compose up -d --force-recreate elasticsearch
