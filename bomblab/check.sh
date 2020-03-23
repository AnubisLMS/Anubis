#!/bin/bash

# Exit on any error
set -e

# resolve path
cd $(dirname $(realpath $0))


check_deps() {
    # acme.json file used by traefik needs specific
    # conditions to work
    if [ ! -d log ]; then
        mkdir -p log
    fi

    # We need to make sure all the files
    # that need to exist do. If they
    # don't exist, we will simply make an
    # empty placeholder.
    files=(
        bomblab-scoreboard.html
        netids.json
        log.txt
        scores.txt
        log/requestd.log
        log/resultd.log
    )

    for i in ${files[@]}; do
        if [ ! -f "${i}" ]; then
            touch ${i}
        fi
    done

    if ! which docker &> /dev/null; then
        echo 'You must install docker'
        echo ''
        echo '  curl https://get.docker.com/ | sh'
        echo ''

        exit 1
    fi

    if ! which docker-compose &> /dev/null; then
        echo 'You must install docker-compose'
        echo ''
        echo '  sudo apt update && sudo apt install -y docker-compose'
        echo ''

        exit 1
    fi

    if ! docker ps &> /dev/null; then
        echo 'You must have the docker daemon running'
        echo ''
        echo '  sudo systemctl start docker.service'
        echo ''

        exit 1
    fi
}

check_env() {
    # We will want to make sure necessary config is loaded
    # if it is not, we should print what is missing, and
    # how to generate it.
    local missing
    missing=0

    if [ -z "${ACME_EMAIL}" ]; then
        echo 'You need to set the ACME_EMAIL environment variable'
        echo 'for the letsencrypt cert'
        echo ''
        echo '  echo export ACME_EMAIL=john.doe@email.com >> .env'
        echo ''
        missing=1
    fi

    if [ -z "${BOMB_AUTH}" ]; then
        echo 'You need to set the BOMB_AUTH  environment variable'
        echo 'for the solutions to be accesable (for TAs)'
        echo ''
        echo '  echo BOMB_AUTH=$(docker run -it httpd htpasswd -Bbn '"'"'<username>'"'"' '"'"'<password>'"'"' | python3 -c '"'"'print(input().strip())'"'"') >> .env'
        echo ''
        missing=1
    fi

    if [ -z "${BOMBLAB_DOMAIN}" ]; then
        echo 'You need to set the DOMAIN environment variable'
        echo ''
        echo '  echo DOMAIN=nyu.cool >> .env'
        echo ''
        missing=1
    fi

    if (( ${missing} == 1 )); then
        # If missing exit
        exit 1
    fi
}

main() {
    # Do basic checks
    check_deps
}

main
