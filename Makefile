#/**************************************************************/
# -- FaTeam Makefile --
# @author: Farsheed Ashouri
# #/**************************************************************/

PYV=$(shell python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)");
PYENVDIR="pyenv"

build:
	@ if test ! -d $(PYENVDIR); then virtualenv $(PYENVDIR); fi
	@ pyenv/bin/pip install -U -r requirements
	
