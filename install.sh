#!/bin/bash

sudo apt-get install python3-venv
python -m venv env
. ./env/bin/activate
pip install pandas plotext Flask flask-restful
