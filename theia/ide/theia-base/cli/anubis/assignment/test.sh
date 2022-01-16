#!/bin/sh

set -e

cd $(dirname $(realpath $0))

if [ ! -d student ]; then
    git clone https://github.com/wabscale/xv6-public.git student
fi

docker build -t registry.digitalocean.com/anubis/assignment/{unique_code} .

docker run -it \
       -e DEBUG=1 \
       -v $(pwd)/student:/student \
       registry.digitalocean.com/anubis/assignment/{unique_code} --repo /student --path ./student $@

