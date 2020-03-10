#!/usr/bin/python3

import sys
import json
import time
from elasticsearch import Elasticsearch

es=Elasticsearch(sys.argv[1])

data = es.search(index='request', size=5000)
json.dump(data, open('./dump-{}.json'.format(time.time()), 'w'))

es.indices.delete(index='request')
#for i in ['request_cli','request_job-request','request_rick-roll', 'request_submission-request']:
for i in ['request']:
    es.indices.create(index=i, body={"mappings":{"properties": {
        "ip": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "location": {
            "type": "geo_point"
        },
        "msg": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "timestamp": {
            "type": "date"
        },
        "type": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        }
    }}})


def f(x):
    l = x['hits']['hits'][:]
    b = []
    for i in l:
        y = i['_source']
        y['index'] = i['_index'] + '_' + y['type']
        #if y['location'] is not None:
        y['location'] = y['location'][::-1]
        b.append(y)
    return b


for i in data['hits']['hits']:
    if 'location' in i['_source'] and i['_source']['location']:
        i['_source']['location'] = i['_source']['location'][::-1]
    try:
        es.index(index='request', body=i['_source'])
    except Exception as e:
        print(i, e)

