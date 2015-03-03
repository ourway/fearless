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


def createCollectionStandards(target, session):
    '''Some operations after getting ID'''
    from flib.models import Collection, Repository
    repository = target.repository
    if not repository:
        repository = session.query(Repository).filter_by(id=target.repository_id).first()
    if target.path:
        target.url = os.path.join(repository.path, target.path)  ## important
        collection_path = os.path.join(repository.path, target.path)
        if not os.path.isdir(collection_path):
            os.makedirs(collection_path)
        thmb = os.path.join(
            os.path.dirname(__file__), '../templates/icons/asset_thumb.png')
        dest = os.path.join(collection_path, 'thumb.png')
        if not os.path.isfile(dest):
            shutil.copyfile(thmb, dest)
    collection = defaultdict(list)
    if target.schema:
        collection = json.loads(target.schema)
    elif target.template:
        templateFile = os.path.join(
            os.path.dirname(__file__), '../templates/collection_templates.json')
        collection = json.loads(
            open(templateFile).read()).get(target.template)

    if collection:

        # print collection.get('folders')
        if collection.get('folders'):
            generated = {}
            target.container = False
            target.holdAssets = False

            for folder in collection.get('folders'):
                newFolder = os.path.join(
                    repository.path, target.path or repository.path, folder)
                if not os.path.isdir(newFolder):
                    try:
                        os.makedirs(newFolder)
                    except OSError:
                        pass
                newCollectionName = os.path.basename(folder).title()
                for part in folder.split('/'):
                    container = False
                    holdAssets = False
                    index = folder.split('/').index(part)
                    if index == len(folder.split('/')) - 1:
                        container = False
                        holdAssets = True
                    if len(folder.split('/')) == 1:
                        container = True
                        holdAssets = False

                    part = part.strip()
                    tn = folder.split('/').index(part)
                    tc = '@@'.join(folder.split('/')[:tn + 1])
                    partPath = os.path.join(
                        repository.path, target.path,  tc.replace('@@', '/'))

                    if not generated.get(tc):
                        newCollection = Collection(name=newCollectionName, path=part,
                                                   repository_id=repository.id,
                                                   container=container, holdAssets=holdAssets)
                        if tn:
                            tcm = '@@'.join(folder.split('/')[:tn])
                            newCollection.parent = generated.get(tcm)
                            #session.add(newCollection)
                        else:
                            newCollection.parent = target
                        generated[tc] = newCollection
                        if 'seq_' in part.lower():
                            part = 'sequence'
                        tdest = os.path.join(partPath, 'thumb.png')
                        tsrc = os.path.join(
                            os.path.dirname(__file__), '../templates/icons/%s.png' % part.lower())
                        if not os.path.isfile(tsrc):
                            tsrc = os.path.join(os.path.dirname(__file__), '../templates/icons/data.png')

                        shutil.copyfile(tsrc, tdest)

        if collection.get('copy'):
            for c in collection.get('copy'):
                src = os.path.join(
                    os.path.dirname(__file__), '../templates/%s' % collection.get('copy')[c])
                dest = os.path.join(
                    repository.path, target.path or repository.path, c)

                if os.path.isfile(src):
                    shutil.copyfile(src, dest)

def collectionFinalFixes(target, session):
    from flib.models import Collection
    parent = session.query(Collection).filter_by(id=target.parent_id).first()
    if parent and parent.path not in target.path:
        newpath = os.path.join(parent.path, target.path)
        target.path = newpath



