#!/bin/sh

if [[ -z "${SKIP_INSTALL}" ]]; then
  echo "To skip install run: SKIP_INSTALL=True ./run_tests.sh"
  pipenv install --dev 
else
  echo "Skipping pipenv install --dev"
fi

pipenv run green -vv --run-coverage --failfast "test" "$@"
