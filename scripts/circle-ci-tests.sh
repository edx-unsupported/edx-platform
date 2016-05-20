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

EXIT=0

case $CIRCLE_NODE_INDEX in
    0)  # run the quality metrics
        echo "Finding fixme's and storing report..."
        paver find_fixme > fixme.log || { cat fixme.log; EXIT=1; }

        echo "Finding pep8 violations and storing report..."
        paver run_pep8 > pep8.log || { cat pep8.log; EXIT=1; }

        echo "Finding pylint violations and storing in report..."
        # HACK: we need to print something to the console, otherwise circleci
        # fails and aborts the job because nothing is displayed for > 10 minutes.
        paver run_pylint -l $PYLINT_THRESHOLD | tee pylint.log || EXIT=1

        # Run quality task. Pass in the 'fail-under' percentage to diff-quality
        paver run_quality -p 100 || EXIT=1

        mkdir -p reports
        echo "Finding jshint violations and storing report..."
        PATH=$PATH:node_modules/.bin
        paver run_jshint -l $JSHINT_THRESHOLD > jshint.log || { cat jshint.log; EXIT=1; }
        echo "Running code complexity report (python)."
        paver run_complexity > reports/code_complexity.log || echo "Unable to calculate code complexity. Ignoring error."

        if [ $EXIT -gt 0 ] ; then
          echo "Exiting command due to quality violations"
          exit $EXIT
        fi

        paver test_lib --extra_args="--with-flaky" --cov_args="-p"
        ;;

    1)  # run all of the lms unit tests
        paver test_system -s lms --extra_args="--attr='shard_1' --with-flaky" --cov_args="-p"
        ;;

    2)  # run all of the cms unit tests
        paver test_system -s cms --extra_args="--with-flaky" --cov_args="-p"
        ;;

    3)  # run the commonlib unit tests
        paver test_system -s lms --extra_args="--attr='shard_1=False' --with-flaky" --cov_args="-p"
        ;;

    *)
        echo "No tests were executed in this container."
        echo "Please adjust scripts/circle-ci-tests.sh to match your parallelism."
        exit 1
        ;;
esac
