#!/bin/sh

pipenv install --dev 

pipenv run green -vv --run-coverage --failfast "test" "$@"
