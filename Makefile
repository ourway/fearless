#/**************************************************************/
# -- FaTeam Makefile --
# @author: Farsheed Ashouri
# #/**************************************************************/

PYENVDIR="pyenv"

build:
	@if test ! -d $(PYENVDIR); then python2.7 -m virtualenv $(PYENVDIR) ;fi
	@pyenv/bin/pip install -U setuptools
	@pyenv/bin/pip install -r requirements

update:
	@pyenv/bin/pip install -U -r requirements

install:
	@yum install gcc libffi-devel python-devel openssl-devel
	#@python2.7 etc/ez_setup.py
	#@python2.7 -m easy_install pip
	#@python2.7 -m pip install -U setuptools
	#@python2.7 -m pip install -U virtualenv
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/supervisor/fateam.template > $(CURDIR)/config/supervisor/fateam.conf
	@find $(CURDIR)/config/supervisor -name *.conf | xargs ln -f -s -t /etc/supervisor/conf.d
