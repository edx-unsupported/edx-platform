#!/usr/bin/env bash
###############################################################################
#
#   circle-ci-tests.sh
#
#   Execute tests for edx-platform on circleci.com
#
#   Forks should configure parallelism, and use this script
#   to define which tests to run in each of the containers.
#
###############################################################################

# From the sh(1) man page of FreeBSD:
# Exit immediately if any untested command fails. in non-interactive
# mode.  The exit status of a command is considered to be explicitly
# tested if the command is part of the list used to control an if,
# elif, while, or until; if the command is the left hand operand of
# an “&&” or “||” operator; or if the command is a pipeline preceded
# by the ! operator.  If a shell function is executed and its exit
# status is explicitly tested, all commands of the function are con‐
# sidered to be tested as well.
set -e

# Return status is that of the last command to fail in a
# piped command, or a zero if they all succeed.
set -o pipefail

# There is no need to install the prereqs, as this was already
# just done via the dependencies override section of circle.yml.
export NO_PREREQ_INSTALL='true'
export BOTO_CONFIG='/tmp/nowhere'
export PYTHONHASHSEED=0


EXIT=0

if [ "$CIRCLE_NODE_TOTAL" == "1" ] ; then
    echo "Only 1 container is being used to run the tests."
    echo "To run in more containers, configure parallelism for this repo's settings "
    echo "via the CircleCI UI and adjust scripts/circle-ci-tests.sh to match."

    echo "Running tests for common/lib/ and pavelib/"
    paver test_lib --cov-args="-p" || EXIT=1
    echo "Running python tests for Studio"
    paver test_system -s cms --cov-args="-p" || EXIT=1
    echo "Running python tests for lms"
    paver test_system -s lms --cov-args="-p" || EXIT=1

    exit $EXIT
else
    # Split up the tests to run in parallel on 4 containers
    case $CIRCLE_NODE_INDEX in
        0)  # run the quality metrics
            echo "Skipping quality"
            ;;

        1)  # run all of the lms unit tests
            paver test_system -s lms --cov-args="-p" --disable-migrations
            ;;

        2)  # run all of the cms unit tests
            echo "Skipping cms"
            ;;

        3)  # run the commonlib and solutions apps unit tests
            echo "Skipping commonlib"
            ;;

        *)
            echo "No tests were executed in this container."
            echo "Please adjust scripts/circle-ci-tests.sh to match your parallelism."
            exit 1
            ;;
    esac
fi
