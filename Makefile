#/**************************************************************/
# -- FaTeam Makefile --
# @author: Farsheed Ashouri
# #/**************************************************************/

PYENVDIR="pyenv"
FFMPEG="2.4.1"
NGINX="1.6.2"
OPENSOURCE="src/api/opensource"

build:
	@if test ! -d $(PYENVDIR); then python2.7 -m virtualenv $(PYENVDIR); fi
	@pyenv/bin/pip install -U setuptools
	@pyenv/bin/pip install -r requirements
	@pyenv/bin/pip install git+https://github.com/hydrogen18/multipart-python
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/supervisor/fateam.template > $(CURDIR)/config/supervisor/fateam.conf
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/uwsgi/api.ini.template > $(CURDIR)/config/uwsgi/api.ini
	@sed 's:{dir}:'`pwd`':' $(CURDIR)/config/nginx/fa_team.conf.template > $(CURDIR)/config/nginx/fa_team.conf
	@if test ! -f $(OPENSOURCE)/contenttype.py; then wget --no-check-certificate  -P $(OPENSOURCE) https://raw.githubusercontent.com/web2py/web2py/2b50cf27e2704ad4b5f20e1e0b71f21d4fd04e20/gluon/contenttype.py; fi
	@wget http://nginx.org/download/nginx-$(NGINX).tar.gz
	@tar xf nginx-$(NGINX).tar.gz
	@mkdir -p bin/nginx
	@cd nginx-$(NGINX); ./configure --prefix=$(CURDIR)/bin/nginx
	@cd nginx-$(NGINX); make
	@cd nginx-$(NGINX); make install
	@if test ! -d bin; then mkdir bin; fi
	@wget -c http://johnvansickle.com/ffmpeg/releases/ffmpeg-$(FFMPEG)-64bit-static.tar.xz
	@tar xvfJ ffmpeg-$(FFMPEG)-64bit-static.tar.xz
	@mv ffmpeg-$(FFMPEG)-64bit-static bin/ffmpeg
	@rm ffmpeg-$(FFMPEG)-64bit-static.tar.xz
	@rm -rf nginx-$(NGINX)

	#wget http://download.redis.io/releases/redis-stable.tar.gz

update:
	@pyenv/bin/pip install -U -r requirements

install:
	#
	@if test -d /etc/rc.d/init.d; then ln -f -s  $(CURDIR)/config/supervisord /etc/rc.d/init.d/supervisord;else ln -f -s  $(CURDIR)/config/supervisord /etc/init.d/supervisord; fi
	@if test -d /etc/rc.d/init.d; then chmod +x /etc/rc.d/init.d/supervisord; else chmod +x /etc/init.d/supervisord; fi
	@if test -f /sbin/insserv; then chkconfig --add supervisord; fi
	@if test -f /sbin/insserv; then chkconfig supervisord on; fi
	@ln -f -s  $(CURDIR)/config/supervisord.conf /etc/supervisord.conf
	#@python2.7 etc/ez_setup.py
	#@python2.7 -m easy_install pip
	#@python2.7 -m pip install -U setuptools
	#@python2.7 -m pip install -U virtualenv
	@mkdir -p /etc/supervisor/conf.d
	@find $(CURDIR)/config/supervisor -name *.conf | xargs ln -f -s -t /etc/supervisor/conf.d
	@find $(CURDIR)/config/nginx -name *.conf | xargs ln -f -s -t /etc/nginx/conf.d
	@mkdir -p embedded
	@service nginx restart
	@service supervisord start
	@supervisorctl update
	@supervisorctl restart fa-team-api
	@supervisorctl restart fa-team-celery
	#@riak-admin bucket-type create siblings_allowed '{"props":{"allow_mult":true}}'
	#@riak-admin bucket-type activate siblings_allowed
	#@riak-admin bucket-type status siblings_allowed
	#@sudo -u postgres createuser -PE vserver
	#@sudo -u postgres createdb -O vserver -E UTF8 vserver

prepare:
	@yum install gcc libffi-devel python-devel openssl-devel postgresql-devel python-pip python-virtualenv pcre-devel -y
	@pip install -U setuptools
	@pip install -U pip virtualenv
	@pip install supervisor

