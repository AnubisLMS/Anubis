#!/bin/bash

cd $(dirname $(realpath $0))

load_env() {
    # Just make sure that .env gets loaded right
    if [ -f .env ]; then
        export $(cat .env | xargs)
    fi
}


check_env() {
    # Checks to make sure necessary env vars are set

    required_env_vars=(
        ACME_EMAIL                 # email for lets encrypt cert
        MYSQL_ROOT_PASSWORD        # mysql database password
        AUTH                       # htpasswd for basic auth
        GF_SECURITY_ADMIN_PASSWORD # grafana password
        DOMAIN                     # domain
    )

    for var_name in ${required_env_vars[@]}; do
        if ! env | grep "^${var_name}=" &> /dev/null; then
            # if var not defined
            echo "ERROR ${var_name} is not defined! This variable is required." 1>&2
            exit 1
        fi
    done

    optional_env_vars=(

    )

    for var_name in ${required_env_vars[@]}; do
        if ! env | grep "^${var_name}=" &> /dev/null; then
            # if var not defined
            echo "ERROR ${var_name} is not defined! This variable is optional." 1>&2
        fi
    done
}


main() {
    load_env
    check_env

    docker-compose up -d traefik db redis
    docker-compose up -d --force-recreate --scale worker=3 api worker
}


main
