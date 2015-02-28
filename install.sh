#!/bin/bash

## Download python 2.7.8 (Fearless needs this version)
wget --no-check-certificate https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tar.xz

## install some packages to compile python
sudo yum groupinstall "Development tools" -y
sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel -y

## extract and cinfigure 
tar xf Python-2.7.8.tar.xz
cd Python-2.7.8
./configure --prefix=/usr/local

## make and install
make
sudo make altinstall





## clean the mess
cd ..
rm -rf Python-2.7.8/
rm -f Python-2.7.8.tar.xz

## download get_pip
wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py

## install pip
sudo python2.7 get-pip.py

## clean mess
rm -f get-pip.py

## install virtualenv
sudo pip install -U virtualenv

## prepare a pyenv
python2.7 -m virtualenv --always-copy pyenv
python2.7 -m virtualenv --relocatable pyenv/

source pyenv/bin/activate
pip install fabric mako
fab -l







