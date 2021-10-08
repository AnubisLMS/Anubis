#!/usr/bin/env sh

export BACKUP_FILE="anubis-$(date +%F_%H%M%S).sql.gz" \
       HOME=/home/anubis

cat /home/anubis/.ssh/config
echo

set -ex

echo 'Creating backup file'
mysqldump \
    --user=anubis \
    --host=${DB_HOST} \
    --port=${DB_PORT} \
    --password=${DB_PASSWORD} \
    anubis \
    | gzip - > /tmp/${BACKUP_FILE}

if [ -n "${SFTP_LOCATION}" ]; then
    echo 'scping file to remote'
    echo "put /tmp/${BACKUP_FILE} ${SFTP_LOCATION}" | sftp ${SFTP_USER}@${SFTP_HOST}
fi

