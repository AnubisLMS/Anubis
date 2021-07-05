#!/bin/sh

# This should be run when testing against a mindebug environment.
# It will set the MINDEBUG environment variable to on, ensuring
# that the tests are pointed to the correct database.

# Change to test directory
cd $(dirname $(realpath $0))

# Set MINDEBUG on
export MINDEBUG=1

# Run normal test script
exec ./test.sh $@