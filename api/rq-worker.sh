#!/bin/sh

echo "starting rq worker"
exec rq worker -u redis://:${REDIS_PASS}@redis-master --results-ttl 5 $@
