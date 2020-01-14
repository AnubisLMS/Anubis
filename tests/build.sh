#!/bin/bash

# This script should build the build image, then the test images.
# Since all the test images will pull from the build image,
# the build order here is importaint.

set -e

cd $(dirname $(realpath $0))

build_build_image() {
    # builds the build image
    docker build -t os3224-build os3224-build &> /dev/null
    echo './os3224-build os3224-build'
}

build_clone_image() {
    # build clone image
    docker build -t os3224-clone os3224-clone &> /dev/null
    echo './os3224-clone os3224-clone'
}

build_report_image() {
    # build report image
    docker build -t os3224-report os3224-report &> /dev/null
    echo './os3224-report os3224-report'
}


build_assignment_images() {
    # builds all the test images
    docker build -t os3224-assignment-base assignments &> /dev/null
    echo './assignments os3224-assignment-base'

    for assignment in $(ls assignments); do
        if [ -d "./assignments/${assignment}" ]; then
            docker build -t "os3224-assignment-${assignment}" "assignments/${assignment}" &> /dev/null
            echo "./assignments/${assignment} os3224-assignment-${assignment}"
        fi
    done
}


main() {
    echo '# building build image' 1>&2
    build_build_image

    echo
    echo '# building clone image' 1>&2
    build_clone_image

    echo
    echo '# building report image' 1>&2
    build_report_image

    echo
    echo '# building assignment images' 1>&2
    build_assignment_images
}

main
