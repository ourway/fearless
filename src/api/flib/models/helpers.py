import os
import shutil
from collections import defaultdict
import ujson as json


def expertizer(name):
    from flib.models import Expert
    _t = Expert.as_unique(name=name)
    return _t


def tag_maker(name):
    from flib.models import Tag
    _t = Tag.as_unique(name=name)
    return _t


def group_maker(name):
    from flib.models import Group
    _t = Group.as_unique(name=name)
    return _t


def departement_maker(name):
    from flib.models import Departement
    _t = Departement.as_unique(name=name)
    return _t


def account_maker(name):
    from flib.models import Account
    _t = Account.as_unique(name=name)
    return _t
