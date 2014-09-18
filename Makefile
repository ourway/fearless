#/**************************************************************/
# -- FaTeam Makefile --
# @author: Farsheed Ashouri
# #/**************************************************************/

PYENVDIR="pyenv"

build:
	@if test ! -d $(PYENVDIR); then python2.7 -m virtualenv $(PYENVDIR) ;fi
	@pyenv/bin/pip install -U setuptools
	@pyenv/bin/pip install -r requirements
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/supervisor/fateam.template > $(CURDIR)/config/supervisor/fateam.conf
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/uwsgi/api.ini.template > $(CURDIR)/config/uwsgi/api.ini
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/nginx/fa_team.conf.template > $(CURDIR)/config/nginx/fa_team.conf

update:
	@pyenv/bin/pip install -U -r requirements

install:
	@yum install gcc libffi-devel python-devel openssl-devel
	#@python2.7 etc/ez_setup.py
	#@python2.7 -m easy_install pip
	#@python2.7 -m pip install -U setuptools
	#@python2.7 -m pip install -U virtualenv
	@find $(CURDIR)/config/supervisor -name *.conf | xargs ln -f -s -t /etc/supervisor/conf.d
	@find $(CURDIR)/config/nginx -name *.conf | xargs ln -f -s -t /etc/nginx/conf.d
	@service nginx restart
	@supervisorctl update
	@supervisorctl restart fa-team-api
