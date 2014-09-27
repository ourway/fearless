#/**************************************************************/
# -- FaTeam Makefile --
# @author: Farsheed Ashouri
# #/**************************************************************/

PYENVDIR="pyenv"
FFMPEG="2.4.1"
OPENSOURCE="src/api/opensource"

build:
	@if test ! -d $(PYENVDIR); then python -m virtualenv $(PYENVDIR); fi
	@pyenv/bin/pip install -U setuptools
	@pyenv/bin/pip install -r requirements
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/supervisor/fateam.template > $(CURDIR)/config/supervisor/fateam.conf
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/uwsgi/api.ini.template > $(CURDIR)/config/uwsgi/api.ini
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/nginx/fa_team.conf.template > $(CURDIR)/config/nginx/fa_team.conf
	@if test ! -f $(OPENSOURCE)/dal.py; then wget -P $(OPENSOURCE) https://raw.githubusercontent.com/web2py/web2py/master/gluon/dal.py; fi
	@if test ! -f $(OPENSOURCE)/reserved_sql_keywords.py;then wget -P $(OPENSOURCE) https://raw.githubusercontent.com/web2py/web2py/master/gluon/reserved_sql_keywords.py; fi
	@if test ! -f $(OPENSOURCE)/contenttype.py; then wget -P $(OPENSOURCE) https://raw.githubusercontent.com/web2py/web2py/master/gluon/contenttype.py; fi
	@wget -c http://johnvansickle.com/ffmpeg/releases/ffmpeg-$(FFMPEG)-64bit-static.tar.xz
	@if test ! -d bin; then mkdir bin; fi
	@tar xvfJ ffmpeg-$(FFMPEG)-64bit-static.tar.xz
	@mv ffmpeg-$(FFMPEG)-64bit-static bin/ffmpeg
	@rm ffmpeg-$(FFMPEG)-64bit-static.tar.xz

update:
	@pyenv/bin/pip install -U -r requirements

install:
	#
	@if test -d /etc/rc.d/init.d; then ln -f -s  $(CURDIR)/config/supervisord /etc/rc.d/init.d/supervisord;else ln -f -s  $(CURDIR)/config/supervisord /etc/init.d/supervisord; fi
	@if test -d /etc/rc.d/init.d; then chmod +x /etc/rc.d/init.d/supervisord; else chmod +x /etc/init.d/supervisord; fi
	@if test -f /sbin/insserv; then chkconfig --add supervisord; fi
	@if test -f /sbin/insserv; then chkconfig supervisord on; fi
	@ln -f -s  $(CURDIR)/config/supervisord.conf /etc/supervisord.conf
	@service supervisord start
	#@python2.7 etc/ez_setup.py
	#@python2.7 -m easy_install pip
	#@python2.7 -m pip install -U setuptools
	#@python2.7 -m pip install -U virtualenv
	@find $(CURDIR)/config/supervisor -name *.conf | xargs ln -f -s -t /etc/supervisor/conf.d
	@find $(CURDIR)/config/nginx -name *.conf | xargs ln -f -s -t /etc/nginx/conf.d
	@service nginx restart
	@supervisorctl update
	@supervisorctl restart fa-team-api
	@supervisorctl restart fa-team-celery
	@riak-admin bucket-type create siblings_allowed '{"props":{"allow_mult":true}}'
	@riak-admin bucket-type activate siblings_allowed
	@riak-admin bucket-type status siblings_allowed
	sudo -u postgres createuser -PE vserver
	sudo -u postgres createdb -O vserver -E UTF8 vserver

prepare:
	@yum install gcc libffi-devel python-devel openssl-devel postgresql-devel python-pip python-virtualenv
	@pip install -U setuptools
	@pip install -U pip virtualenv
	@pip install supervisor

