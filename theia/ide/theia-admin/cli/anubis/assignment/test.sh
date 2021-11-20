#!/bin/sh

set -e

cd $(dirname $(realpath $0))

if [ ! -d student ]; then
    git clone https://github.com/wabscale/xv6-public.git student
fi

# copy student directory into container
sed -i 's/# COPY student \/student/COPY student \/student/' Dockerfile

anubis assignment build

# Reset it after building to make sure it doens't make it into prod
sed -i 's/^COPY student \/student/# COPY student \/student/' Dockerfile


docker run -it \
       -e DEBUG=1 \
       -v $(pwd)/student:/student \
       registry.digitalocean.com/anubis/assignment/{unique_code} $@

