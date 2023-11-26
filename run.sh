#!/bin/bash

python -m venv env
. ./env/bin/activate
python ./logger.py $1 $2 $3