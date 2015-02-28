#!/bin/bash

## prepare a pyenv
python2.7 -m virtualenv --always-copy pyenv
python2.7 -m virtualenv --relocatable pyenv/

source pyenv/bin/activate
pip install fabric mako
fab -l


