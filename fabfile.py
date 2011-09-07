#!/usr/bin/env python
#-*- coding:utf-8 -*-


from fabric.api import *

def bootstrap():
	local('virtualenv --no-site-packages env', capture=False)
	local('env/bin/pip install -r requirements.ini', capture=False)

