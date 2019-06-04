#!/bin/sh

if [[ -z "${INSTALL}" ]]; then
  echo "Skippign pipenv install --dev"
  echo "To install run: INSTALL=True ./run_tests.sh"
else
  pipenv install --dev 
fi

pipenv run green -vv --run-coverage --failfast "test" "$@"
