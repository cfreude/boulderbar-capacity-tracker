#!/bin/bash

python -m venv env
. ./env/bin/activate
export FLASK_APP=api.py
flask run --host=0.0.0.0 --port=80
