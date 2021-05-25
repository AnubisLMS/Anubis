#!/usr/bin/env sh

export BACKUP_FILE="anubis-$(date +%F_%H%M%S).sql.gz" \
       HOME=/home/anubis

cat /home/anubis/.ssh/config

set -ex

echo 'Creating backup file'
mysqldump \
    -u anubis \
    -h ${DB_HOST} \
    --password=${DATABASE_PASSWORD} \
    --skip-create-options \
    anubis \
    | gzip - > /tmp/${BACKUP_FILE}

if [ -n "${BACKUP_SSH_DOMAIN}" ]; then
    echo 'scping file to remote'
    scp /tmp/${BACKUP_FILE} ${BACKUP_SSH_DOMAIN}/${BACKUP_FILE}
fi

echo 'copying to DO volume'
cp /tmp/${BACKUP_FILE} /mnt/backups/${BACKUP_FILE}
