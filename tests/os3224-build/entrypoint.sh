#!/bin/bash

# This is the entrypoint for the test images. It expects that there are test scripts
# in the working directory (/tmp/build)

# The entrypoint for the assignment test images should not be changed.
# The assignment images should just add their test scripts to the image.


if (( $# < 1 )); then
    echo "xv6 repo is required" 1>&2
    echo "docker run -it os3224-build <git repo url>" 1>&2
    exit 1
fi


build() {
    # clone the repo then build the xv6.img file and move it to a more convientent place

    # clone
    REPO_URL="${1}"
    git clone ${REPO_URL} xv6-public
    cd xv6-public

    # build
    make xv6.img

    # move
    cd ../
    mv ./xv6-public/xv6.img ./

    # clean
    rm -rf xv6-public

    echo 'built xv6.img'
}


run_test() {
    # run each of the test scripts (all scripts matching test-*.sh)
    for test_script in $(ls test-*.sh | sort); do
        bash ${test_script} > ${test_script}.out
    done
}


result_json() {
    # So yeah...
    # I'm rolling my own json in bash...
    # Don't yell at me
    # https://pics.me.me/mom-come-pick-me-up-im-scared-any-minor-inconvenience-43409297.png

    echo -n '{"results":{'
    test_num=0
    for output_file in $(ls test-*.sh.out | sort); do
        if (( test_num != 0 )); then echo -n ','; fi
        echo -n '"test-'${test_num}'":"'$(cat ${output_file} | base64 -d)'"'
    echo -n '}}'
}


report_results() {
    # report results to the api
    curl http://api:5000/private/report-results -XPOST --data "$(result_json)"
}


main() {
    # Build that image
    build

    # Run those tests
    run_tests

    # Report those results
    report_results
}

main
