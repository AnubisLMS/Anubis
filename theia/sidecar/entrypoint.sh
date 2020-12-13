#!/bin/sh

set -e

if [ -n "${GIT_CRED}" ]; then
    echo "${GIT_CRED}" > /home/theia/.git-credentials
    git config --global credential.store helper
    git config --global user.email noreply@anubis.osiris.services
    git config --global user.username os3224-robot
fi

chown -R theia:theia /home/theia

set -x

echo "*/5 * * * * /autosave.sh" | crontab -u theia -
exec /usr/sbin/fcron --debug --foreground
