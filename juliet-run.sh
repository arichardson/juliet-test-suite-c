#!/bin/sh

# the first parameter of this script is either an integer or the string "all".
# if given a number, it will target a subdirectory *in its directory* that
# contains test cases correspding to that CWE number.  if given "all", it will
# target all subdirectories *in its directory* containing CWE test cases.

# the second parameter is optional and specifies a timeout duration. the
# default value is .01 seconds.

# this script will run all good and bad tests in the targeted subdirectories
# and write the names of the tests and their return codes into the files
# "good.run" and "bad.run", both located in the subdirectories. all tests are
# run with a timeout so that tests requiring input terminate quickly with
# return code 124.

ulimit -c 0 # TODO no core dumps for now

SCRIPT_DIR=$(dirname $(realpath "$0"))
TIMEOUT=".01s"

if [ $# -lt 1 ]
then
  echo "need to specify target - see source comments for help"
  exit
fi

TARGET="$1"
if [ $# -ge 2 ]
then
  TIMEOUT="$2"
fi

# parameter 1: the CWE directory corresponding to the tests
# parameter 2: the type of tests to run (should be "good" or "bad")
run_tests()
{
  local CWE_DIRECTORY="$1"
  local TEST_TYPE="$2"
  local TYPE_PATH="${CWE_DIRECTORY}/${TEST_TYPE}"

  local PREV_CWD=$(pwd)
  cd "${CWE_DIRECTORY}" # change directory in case of test-produced output files

  echo "========== STARTING TEST ${TYPE_PATH} $(date) ==========" >> "${TYPE_PATH}.run"
  for TESTCASE in $(ls -1 "${TYPE_PATH}"); do
    local TESTCASE_PATH="${TYPE_PATH}/${TESTCASE}"
    timeout "${TIMEOUT}" "${TESTCASE_PATH}" 0 # timeout requires an argument after the command
    echo "${TESTCASE_PATH} $?" >> "${TYPE_PATH}.run"
  done

  cd "${PREV_CWD}"
}

if [ "${TARGET}" = "all" ]
then
  for DIRECTORY in $(ls -1 "${SCRIPT_DIR}"); do
    if [ $(expr "${DIRECTORY}" : "^CWE[0-9][0-9]*$") -ne 0 ] # make sure this is a CWE directory
    then
      FULL_PATH="${SCRIPT_DIR}/${DIRECTORY}"
      run_tests "${FULL_PATH}" "good"
      run_tests "${FULL_PATH}" "bad"
    fi
  done
elif [ -d "${SCRIPT_DIR}/CWE${TARGET}" ]
then
  FULL_PATH="${SCRIPT_DIR}/CWE${TARGET}"
  run_tests "${FULL_PATH}" "good"
  run_tests "${FULL_PATH}" "bad"
else
  echo "specified target did not correspond to a built CWE testcase directory - see source comments for help"
  exit
fi
