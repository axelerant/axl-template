#!/usr/bin/env bash

set -ex

rm -rf  build/* dist/*
python -m pep517.build .
twine upload dist/*
