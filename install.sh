#!/bin/bash

## Download python 2.7.8 (Fearless needs this version)
wget --no-check-certificate https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tar.xz

## install some packages to compile python
yum groupinstall "Development tools" -y
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel -y

## extract and cinfigure 
tar xf Python-2.7.8.tar.xz
cd Python-2.7.8
./configure --prefix=/usr/local

## make and install
make && make altinstall


## clean the mess
cd ..
rm -rf Python-2.7.8/
rm -f Python-2.7.8.tar.xz


