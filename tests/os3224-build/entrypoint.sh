#!/bin/bash

# docker run -it os3224-build <commit>

# This is the entrypoint for the test images. It expects that there are test scripts
# in the working directory (/tmp/build)

# The entrypoint for the assignment test images should not be changed.
# The assignment images should just add their test scripts to the image.

set -e

if (( $# < 1 )); then
    echo "git commit is required" 1>&2
    echo "docker run -it os3224-build <commit> [<files to copy>]" 1>&2
    exit 1
fi


COMMIT="${1}"
shift
FILES="$@"

build() {
    # build the xv6.img file and move it to a more convientent place

    cd /mnt/submission/build

    git checkout "${COMMIT}"
    rm -rf .git # ah yeet

    # overwrite the README with lorem ipsum
    python3 /overwrite.py

    # build
    make clean ${FILES}

    # move
    cd ../
    for f in ${FILES}; do
        mv ./build/$f ./
    done

    # clean
    rm -rf build
}

main() {
    # Build that image
    build

    # Sanity check that there
    # are no forged reports
    forged="$(find . -name '*-report.json')"
    if [ -n "${forged}" ]; then
        rm -rf ${forged}
    fi

    # report success
    echo
    echo 'Successfully built xv6.img!'
    echo
}

main
