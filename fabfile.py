from fabric.api import run, env, hosts, local, task, cd, lcd, settings, prompt, sudo

import os
import shutil
from mako.template import Template

nginx_version = '1.7.10'
redis_version = '2.8.19'
ruby_version = '2.2.0'
openssl_version = '1.0.2'

dataname = 'fearless1'


#env.hosts = ['fearless@192.168.20.159', 'fearless@192.168.20.151']

#@hosts('fearless@192.168.20.159')

#@task
#def localhost():

env.run = local
env.hosts = ['localhost']
env.cd = lcd

@task
def remote():
    env.run = run
    env.hosts = ['some.remote.host']
    env.cd = cd
    'Not Implemented'


def _get_pwd():
    return os.path.abspath(os.path.dirname(__file__))

def _make_downloads_folder():
    dfolder = '%s/.downloads' % _get_pwd()
    if not os.path.isdir(dfolder):
        os.makedirs(dfolder)
    return dfolder




def _download_nginx():
    '''Download nginx'''
    print('Getting nginx ...')
    dfolder = _make_downloads_folder()
    nginx_file = '%s/nginx-%s.tar.gz' % (dfolder, nginx_version)
    if not os.path.isfile(nginx_file):
        with env.cd(dfolder):
            print env.run('ls -l')
            nginx_download_link = 'http://nginx.org/download/nginx-%s.tar.gz' % nginx_version
            download_cmd = 'wget %s' % nginx_download_link
            env.run(download_cmd)
            print('Finished downloading nginx')
    else:
        print('Using cached nginx')
    return nginx_file


def _download_java():
    '''Download java'''
    print('Getting java ...')
    dfolder = _make_downloads_folder()
    nginx_file = '%s/nginx-%s.tar.gz' % (dfolder, nginx_version)
    if not os.path.isfile(nginx_file):
        with env.cd(dfolder):
            print env.run('ls -l')
            nginx_download_link = 'http://nginx.org/download/nginx-%s.tar.gz' % nginx_version
            download_cmd = 'wget %s' % nginx_download_link
            env.run(download_cmd)
            print('Finished downloading nginx')
    else:
        print('Using cached nginx')
    return nginx_file

@task
def install_basho_repo():
    #!/bin/bash

    HOSTNAME='basho_riak'
    FILENAME='/etc/yum.repos.d/basho.repo'
    OS='el'
    DIST='5'
    PACKAGE_CLOUD_RIAK_DIR='https://packagecloud.io/install/repositories/basho/riak'
    cmd = '''curl "%s/config_file.repo?os=%s&dist=%s&name=%s" > %s''' %\
        (PACKAGE_CLOUD_RIAK_DIR, OS, DIST, HOSTNAME, FILENAME)
    po_info = sudo(cmd)
    

def _download_openssl():
    '''Download openssl'''
    print('Getting openssl ...')
    dfolder = _make_downloads_folder()
    openssl_file = '%s/openssl-%s.tar.gz' % (dfolder, openssl_version)
    if not os.path.isfile(openssl_file):
        with env.cd(dfolder):
            openssl_download_link = 'https://www.openssl.org/source/openssl-%s.tar.gz' % openssl_version
            download_cmd = 'wget %s' % openssl_download_link
            env.run(download_cmd)
            print('Finished downloading openssl')
    else:
        print('Using cached openssl')
    return openssl_file


def _download_redis():
    '''Download redis'''
    print('Getting redis ...')
    dfolder = _make_downloads_folder()
    redis_file = '%s/redis-%s.tar.gz' % (dfolder, redis_version)
    if not os.path.isfile(redis_file):
        with env.cd(dfolder):
            redis_download_link = 'http://download.redis.io/releases/redis-%s.tar.gz' % redis_version
            download_cmd = 'wget %s' % redis_download_link
            env.run(download_cmd)
            print('Finished downloading redis')
    else:
        print('Using cached redis')
    return redis_file


def _download_ffmpeg():
    '''Download ffmpeg'''
    print('Getting ffmpeg ...')
    dfolder = _make_downloads_folder()
    ffmpeg_file = '%s/ffmpeg-release-64bit-static.tar.xz' % (dfolder)
    if not os.path.isfile(ffmpeg_file):
        with env.cd(dfolder):
            ffmpeg_download_link = 'http://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz'
            download_cmd = 'wget %s' % ffmpeg_download_link
            env.run(download_cmd)
            print('Finished downloading ffmpeg')
    else:
        print('Using cached ffmpeg')
    return ffmpeg_file

def _download_ruby():
    '''Download ruby'''
    print('Getting ruby ...')
    dfolder = _make_downloads_folder()
    ruby_file = '%s/ruby-%s.tar.gz' % (dfolder, ruby_version)
    if not os.path.isfile(ruby_file):
        with env.cd(dfolder):
            ruby_download_link = 'http://cache.ruby-lang.org/pub/ruby/2.2/ruby-%s.tar.gz' % ruby_version
            download_cmd = 'wget %s' % ruby_download_link
            env.run(download_cmd)
            print('Finished downloading ruby')
    else:
        print('Using cached ruby')
    return ruby_file


def _get_nginx_config():
    temp = Template(filename='%s/config/nginx/nginx.conf.tml' % _get_pwd())
    conf = temp.render(dir=_get_pwd())
    with open('%s/bin/nginx/conf/nginx.conf' % _get_pwd(), 'wb') as f:
        f.write(conf)


def _get_supervisord_config():
    temp = Template(filename='%s/config/supervisor/fearless.conf.tml' % _get_pwd())
    conf = temp.render(dir=_get_pwd())
    #print conf
    with open('%s/config/supervisor/fearless.conf' % _get_pwd(), 'wb') as f:
        f.write(conf)

    output = env.run('echo_supervisord_conf', capture=True)
    with open('/home/farsheed/Desktop/testC.txt', 'wb') as f:
        f.write(output + conf)
    sudo('rm /etc/supervisord.conf')
    sudo('ln -s /home/farsheed/Desktop/testC.txt /etc/supervisord.conf')


def _install_nginx():
    '''install nginx'''
    nginx_file = _download_nginx()
    if os.path.isfile('%s/bin/nginx/sbin/nginx' % _get_pwd()):
        print 'nginx Already installed.'
    else:
        with env.cd(os.path.dirname(nginx_file)):
            env.run('tar xf %s'%os.path.basename(nginx_file))
            with env.cd('nginx-%s'%nginx_version):
                nginx_install_folder = '%s/bin/nginx' % _get_pwd()
                if not os.path.isdir(nginx_install_folder):
                    os.makedirs(nginx_install_folder)
                env.run('./configure --prefix="%s" --with-http_gzip_static_module' % nginx_install_folder)
                env.run('make')
                env.run('make install')
                env.run('make clean')
        assert os.path.isfile('%s/bin/nginx/sbin/nginx' % _get_pwd())

            #shutil.rmtree('redis-%s'%redis_version)
    _get_nginx_config()


def _install_redis():
    '''install redis'''
    redis_file = _download_redis()
    if os.path.isfile('%s/bin/redis/bin/redis-server' % _get_pwd()):
        print 'redis Already installed.'
    else:
        with env.cd(os.path.dirname(redis_file)):
            env.run('tar xf %s'%os.path.basename(redis_file))
            with env.cd('redis-%s'%redis_version):
                redis_install_folder = '%s/bin/redis' % _get_pwd()
                if not os.path.isdir(redis_install_folder):
                    os.makedirs(redis_install_folder)
                env.run('make')
                env.run('make PREFIX="%s" install' % redis_install_folder)
                env.run('make clean')
        assert os.path.isfile('%s/bin/redis/bin/redis-server' % _get_pwd())
            #shutil.rmtree('redis-%s'%redis_version)


def _install_ffmpeg():
    '''install ffmpeg'''
    ffmpeg_file = _download_ffmpeg()
    if os.path.isfile('%s/bin/ffmpeg/ffmpeg' % _get_pwd()):
        print 'ffmpeg Already installed.'
    else:

        with env.cd(os.path.dirname(ffmpeg_file)):
            ffmpeg_install_folder = '%s/bin/ffmpeg' % _get_pwd()
            if not os.path.isdir(ffmpeg_install_folder):
                os.makedirs(ffmpeg_install_folder)
            env.run('tar xvfJ %s' % ffmpeg_file)
            with env.cd('ffmpeg*'):
                env.run('cp -rf * %s'%ffmpeg_install_folder)
        assert os.path.isfile('%s/bin/ffmpeg/ffmpeg' % _get_pwd())


def _install_ruby():
    '''install ruby'''
    ruby_file = _download_ruby()
    if os.path.isfile('%s/bin/ruby/bin/ruby' % _get_pwd()):
        print 'ruby Already installed.'
    else:
        with env.cd(os.path.dirname(ruby_file)):
            env.run('tar xf %s'%os.path.basename(ruby_file))
            with env.cd('ruby-%s'%ruby_version):
                ruby_install_folder = '%s/bin/ruby' % _get_pwd()
                if not os.path.isdir(ruby_install_folder):
                    os.makedirs(ruby_install_folder)
                env.run('./configure --prefix="%s"' % ruby_install_folder)
                env.run('make')
                env.run('make install')
                env.run('make clean')
        assert os.path.isfile('%s/bin/ruby/bin/ruby' % _get_pwd())

    ## now lets install task juggler
    print 'Installing taskjuggler'
    if os.path.isfile('%s/bin/ruby/bin/tj3' % _get_pwd()):
        print 'taskjuggler Already installed.'
    else:
        env.run('%s/bin/ruby/bin/gem install taskjuggler' % _get_pwd())
        assert os.path.isfile('%s/bin/ruby/bin/tj3'%_get_pwd())

def _createMysqlDb():
    #print env
    with settings(warn_only=True):
        env.run('echo "CREATE DATABASE %s;"|mysql --batch --user=%s --password=%s --host=%s'\
            % (dataname, env.mysqluser, env.mysqlpassword, env.host))

def _dropMysqlDb():
    #print env
    with settings(warn_only=True):
        env.run('echo "DROP DATABASE %s;"|mysql --batch --user=%s --password=%s --host=%s'\
            % (dataname, env.mysqluser, env.mysqlpassword, env.host))

def _prepareDatabase():
    env.mysqluser = prompt('What is your MySQL user?', default='root')
    env.mysqlpassword = prompt('What is your MySQL password?')
    _dropMysqlDb()
    _createMysqlDb()

@task
def install():
    _install_nginx()
    _install_redis()
    _install_ffmpeg()
    _install_ruby()
    _get_supervisord_config()
    _prepareDatabase()



@task
def update():
    with env.cd(_get_pwd()):
        env.run('{d}/pyenv/bin/pip install -U -r {d}/requirements'.format(d=_get_pwd()))







