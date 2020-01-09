#!/bin/bash

PYTHON3=python3

# From: https://stackoverflow.com/questions/59895/get-the-source-directory-of-a-bash-script-from-within-the-script-itself
THISSCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Setting the Python path
OPENSCHCDIR="$(dirname $(dirname ${THISSCRIPTDIR} ))"
export PYTHONPATH=${OPENSCHCDIR}/src

# Now running the code
${PYTHON3} ${THISSCRIPTDIR}/test_simul.py
