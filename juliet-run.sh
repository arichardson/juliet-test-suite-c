#!/bin/sh

# the first parameter specifies a non-default timeout duration
# the second parameter specifies the path of a library to LD_CHERI_PRELOAD when running test cases

# this script will run all good and bad tests in the bin subdirectory and write
# the names of the tests and their return codes into the files "good.run" and
# "bad.run". all tests are run with a timeout so that tests requiring input
# terminate quickly with return code 124.

ulimit -c 0

SCRIPT_DIR=$(dirname $(realpath "$0"))
TIMEOUT="1s"
PRELOAD_PATH=""
INPUT_FILE="/tmp/in.txt"

if [ $# -ge 2 ]
then
  TIMEOUT="$2"
fi

if [ $# -ge 3 ]  # actually this argument is not used when juliet.py executes this script via popen() without passing the additional PRELOAD_PATH argument
then
  PRELOAD_PATH="$3"
  if [ ! -f "${PRELOAD_PATH}" ]
  then
    echo "preload path ${PRELOAD_PATH} does not exist - not running tests"
    exit 1
  fi
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

    if [ ! -z "${PRELOAD_PATH}" ]
    then
      timeout "${TIMEOUT}" env LD_CHERI_PRELOAD="${PRELOAD_PATH}" "${TESTCASE_PATH}" < "${INPUT_FILE}"
    else
      timeout "${TIMEOUT}" "${TESTCASE_PATH}" < "${INPUT_FILE}"
    fi

    echo "${TESTCASE_PATH} $?" >> "${TYPE_PATH}.run"
  done

  cd "${PREV_CWD}"
}

run_tests "${SCRIPT_DIR}/CWE${1}" "good" # when the run() is called by juliet.py, script_dir is already in the bin directory and cannot be spliced with bin as a subdirectory , so $1 is actually is CWE-ID directory
run_tests "${SCRIPT_DIR}/CWE${1}" "bad"
