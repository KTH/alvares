#!/bin/sh

EXIST=`command -v pipenv`

if [ -z $EXIST ]; then
    pipenv install --dev 
else 
    echo "pipenv install --dev already run"; 
fi

pipenv run green -vv --run-coverage --failfast "test" "$@"
