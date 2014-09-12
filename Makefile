#/**************************************************************/
# -- FaTeam Makefile --
# @author: Farsheed Ashouri
# #/**************************************************************/

PYENVDIR="pyenv"

build:
	@python src/etc/ez_setup.py
	@python -m easy_install pip
	@python -m pip install -U setuptools
	@python -m pip install -U virtualenv
	@if test ! -d $(PYENVDIR); then python -m virtualenv $(PYENVDIR) ;fi
	@pyenv/bin/pip install -r requirements

update:
	@pyenv/bin/pip install -U -r requirements
	
