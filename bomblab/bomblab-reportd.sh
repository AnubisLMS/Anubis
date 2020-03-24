#!/bin/bash

# This script will simply read all the events out of the database into the log.txt file,
# then use that data to update bomblab-scoreboard.html, and scores.txt.

while true; do
    mysql -h db -u root --password=password -r bomblab <<< 'SELECT ip, `date`, userid, userpwd, labid, `result` FROM Submission' \
        | awk 'NR>1' | tr '\t' '|' > log.txt
    ./bomblab-update.pl
    sleep 30
done
