#!/bin/bash

python -m venv env
. ./env/bin/activate
python ./tracker.py $1 $2