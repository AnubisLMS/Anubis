#!/usr/bin/python3

import sys
import json
import time
from elasticsearch import Elasticsearch

es=Elasticsearch(sys.argv[1])

data = es.search(index='submission', size=5000)
json.dump(data, open('./dump-{}.json'.format(time.time()), 'w'))

es.indices.delete(index='submission')
es.indices.create(index='submission', body={
    "mappings": {
        "properties": {
            "assignment": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "commit": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "error": {
                "type": "long"
            },
            "netid": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "passed": {
                "type": "long"
            },
            "processed": {
                "type": "long"
            },
            "report": {
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
            }
        }
    }
})


for i in data['hits']['hits']:
    try:
        es.index(
            index='submission',
            body={
                'netid': i['_source']['submission']['netid'],
                'commit': i['_source']['submission']['commit'],
                'assignment': i['_source']['submission']['assignment'],
                'timestamp': i['_source']['timestamp'],
                'processed': 0,
                'report': None,
                'error': -1,
                'passed': -1,
            }
        )
    except KeyError:
        print('key error:', i)
