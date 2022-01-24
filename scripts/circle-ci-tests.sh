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
    # Split up the tests to run in parallel on 8 containers
    case $CIRCLE_NODE_INDEX in
        0)  # run the quality metrics
            echo "Finding fixme's and storing report..."
            paver find_fixme > fixme.log || { cat fixme.log; EXIT=1; }

            echo "Finding PEP 8 violations and storing report..."
            paver run_pep8 > pep8.log || { cat pep8.log; EXIT=1; }

            echo "Finding pylint violations and storing in report..."
            # HACK: we need to print something to the console, otherwise circleci
            # fails and aborts the job because nothing is displayed for > 10 minutes.
            paver run_pylint -l $LOWER_PYLINT_THRESHOLD:$UPPER_PYLINT_THRESHOLD | tee pylint.log || EXIT=1

            mkdir -p reports
            PATH=$PATH:node_modules/.bin

            echo "Finding ESLint violations and storing report..."
            paver run_eslint -l $ESLINT_THRESHOLD > eslint.log || { cat eslint.log; EXIT=1; }

            echo "Finding Stylelint violations and storing report..."
            paver run_stylelint -l $STYLELINT_THRESHOLD > stylelint.log || { cat stylelint.log; EXIT=1; }

            # Run quality task. Pass in the 'fail-under' percentage to diff-quality
            paver run_quality -p 99 || EXIT=1

            echo "Running code complexity report (python)."
            paver run_complexity > reports/code_complexity.log || echo "Unable to calculate code complexity. Ignoring error."

            exit $EXIT
            ;;

        1)  # run discussion of the lms unit tests
            paver test_system -s lms --pyargs -t discussion --cov-args="-p" --disable-migrations
            ;;

        2)  # run all of the cms unit tests
            paver test_system -s cms --cov-args="-p" --disable-migrations
            ;;

        3)  # run the commonlib and solutions apps unit tests
            paver test_lib
            paver test_system -s lms --pyargs -t edx_solutions_api_integration --disable-migrations
            paver test_system -s lms --pyargs -t edx_solutions_organizations --disable-migrations
            paver test_system -s lms --pyargs -t edx_solutions_projects --disable-migrations
            paver test_system -s lms --pyargs -t gradebook --disable-migrations
            paver test_system -s lms --pyargs -t social_engagement --disable-migrations
            paver test_system -s lms --pyargs -t course_metadata --disable-migrations
            paver test_system -s lms --pyargs -t mobileapps --disable-migrations
            ;;
        4)  # run course_api, grades, course_home_api of the lms unit tests
            paver test_system -s lms --pyargs -t course_api --cov-args="-p" --disable-migrations
            paver test_system -s lms --pyargs -t grades --cov-args="-p" --disable-migrations
            paver test_system -s lms --pyargs -t course_home_api --cov-args="-p" --disable-migrations
            ;;
        5)  # run course_blocks, learner_dashboard of the lms unit tests
            paver test_system -s lms --pyargs -t course_blocks --cov-args="-p" --disable-migrations
            paver test_system -s lms --pyargs -t learner_dashboard --cov-args="-p" --disable-migrations
            ;;
        6)  # run mobile_api, instructor of the lms unit tests
            paver test_system -s lms --pyargs -t mobile_api --cov-args="-p" --disable-migrations
            paver test_system -s lms --pyargs -t instructor --cov-args="-p" --disable-migrations
            ;;
        7)  # run dashboard, courseware of the lms unit tests
            paver test_system -s lms --pyargs -t dashboard --cov-args="-p" --disable-migrations
            paver test_system -s lms --pyargs -t courseware --cov-args="-p" --disable-migrations
            ;;
        *)
            echo "No tests were executed in this container."
            echo "Please adjust scripts/circle-ci-tests.sh to match your parallelism."
            exit 1
            ;;
    esac
fi
