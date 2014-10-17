#!/usr/bin/env python
# -*- coding: utf-8 -*-
_author = 'Farsheed Ashouri'
'''
   ___              _                   _ 
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an appology! 
Clean code is much better than Cleaner comments!
'''

import functools
import logging

def decorator(d):
    """Make function d a decorator: d wraps a function fn.
     Peter Norvig, my good friend at Dropbox"""
    def _d(fn):
        return functools.update_wrapper(d(fn), fn)
    functools.update_wrapper(_d, d)
    return _d


@decorator
def Memoized(func):
    """Decorator that caches a function's return value  PS: Results
      This function is the reason I love python.
      without cache: 7.6e-06
      with cache: 3.2e-07
    """
    cache = {}
    key = (func.__module__, func.__name__)
    # print key
    if key not in cache:
        cache[key] = {}
    mycache = cache[key]

    def _f(*args):
        try:
            return mycache[args]
        except KeyError:
            value = func(*args)
            mycache[args] = value
            return value
        except TypeError:
            return func(*args)

    _f.cache = cache
    return _f


def setup_logger(logger_name, log_file, level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(module)s|%(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    #streamHandler = logging.StreamHandler()
    # streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)

    # l.addHandler(streamHandler)
    return l
