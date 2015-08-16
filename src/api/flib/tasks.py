#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   ___              _                   _
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an apology!
Clean code is much better than Cleaner comments!
'''

'''
@desc: tasks.py
@c: Chista Co
@author: F.Ashouri
@version: 0.1.8
'''

#from gevent import monkey; monkey.patch_all()
import json as json
import hashlib
import base64
import shutil
from datetime import datetime

import requests
import os
import uuid
from envelopes import Envelope, GMailSMTP
from flib.utils.validators import email_validator
from flib.models import fdb
from flib.models.db import session_factory
Session = session_factory
from opensource.contenttype import contenttype
# riak bucket for our files
import sh
from mako.template import Template
from flib.utils.fagit import GIT
from sqlalchemy.exc import IntegrityError  # for exception handeling
from mako.template import Template
from flib.utils.defaults import public_upload_folder, public_repository_path, GIT_folder, ASSETS

current_dir = os.path.abspath(os.path.dirname(__file__))
ffmpeg = os.path.join(current_dir, '../../../bin/ffmpeg/ffmpeg')
ffprobe = os.path.join(current_dir, '../../../bin/ffmpeg/ffprobe')


templates_folder = os.path.join(os.path.dirname(__file__), 'templates')
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# BACKEND_URL = 'amqp'
# BACKEND_URL = 'redis://localhost:6379/0'


BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery
#CELERY_ACCEPT_CONTENT = ['json']
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
from flib.utils.validators import checkPath, md5_for_file


Capp = Celery('tasks',
              broker=BROKER_URL,
              backend=BACKEND_URL,
              include=[])


def process(cmd):
    '''General external process'''
    from subprocess import Popen, PIPE, call  # everything nedded to handle external commands
    p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE,
              )
    # universal_newlines=True)  # process
    (stdout, stderr) = p.communicate()
    return (stdout, stderr)


@Capp.task
def download(url):
    basename = url.split('/')[-1]
    r = requests.head(url)
    length = r.headers.get('content-length')
    if length:  # there is something
        length = int(length) / 1024.0
        data = {'message': 'OK', 'length': length,
                'basename': basename}
    else:
        data = {'message': 'ERROR'}
    return json.dumps(data)


class mydatatype(object):
    pass


@Capp.task
def remove_asset(name):
    pass


@Capp.task
def send_envelope(to, cc, bcc, subject, message, reply_to=None, attach=None):

    _et = os.path.join(templates_folder, 'email.html')
    ET = Template(filename=_et)
    M = ET.render(message=message, subject=subject)
    if not reply_to:
        reply_to='farsheed.ashouri@gmail.com'
    envelope = Envelope(
        from_addr=(u'farsheed.ashouri@gmail.com',
                   u'Fearless Notifications'),
        to_addr=to,
        cc_addr=cc,
        bcc_addr=bcc,
        subject=subject,
        html_body=M,
        headers = {'Reply-To': reply_to}
    )
    #envelope.add_attachment('/home/farsheed/Desktop/guntt.html', mimetype="text/html")

    if attach and os.path.isfile(attach):
        envelope.add_attachment(attach)

    pwd = '\n=MnbvlGdjVmalJlcvZUekFWZSVmY'[::-1]

    gmail = GMailSMTP('farsheed.ashouri@gmail.com',
                      base64.decodestring(pwd))
    gmail.send(envelope)


@Capp.task()
def show_secrets(stream):
    return stream


###########################################################################
def duration(path):
    '''Find video duration'''
    path = path.encode("utf-8")
    arg = '''nice "%s" -show_format "%s" 2>&1''' % (ffprobe, path)
    pr = process(arg)
    dupart = pr[0].split('duration=')  # text processing output of a file
    if pr and len(dupart) > 1:
        du = dupart[1].split()[0]
        try:
            return float(du)
        except ValueError:
            return


@Capp.task
def generateAudioThumbnail(path, assetUuid, version):

    #from flib.utils.svt import create_png as wav2png
    path = path.encode("utf-8")
    #wav2png(output_filename_w=None, output_filename_s=None, image_width=146, image_height=110, fft_size=2048, f_max=22050, f_min=10, wavefile=0, palette=1, channel=1, window="hanning", logspec=0)


@Capp.task
def addFileToGit(path, assetUuid, version):

    path = path.encode("utf-8")
    directory = os.path.dirname(path)
    git_dir = os.path.join(GIT_folder, assetUuid)
    filename = os.path.basename(path)
    # initilize
    command = 'init'
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(
        d=directory, g=git_dir, c=command)
    process(arg)
    # add file
    command = 'add "%s"' % filename
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(
        d=directory, g=git_dir, c=command)
    process(arg)
    # add tag based on new version and uuid
    # commit
    command = 'commit -m "file: %s added."' % filename
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(
        d=directory, g=git_dir, c=command)
    commit, error = process(arg)
    command = 'tag v_%s' % version
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(
        d=directory, g=git_dir, c=command)
    process(arg)
    # now lets clone it to assets folder
    asset_folder = os.path.join(ASSETS, assetUuid)
    if not os.path.isdir(asset_folder):  # not cloned
        command = 'git clone -l "%s" "%s"' % (git_dir, asset_folder)
        process(command)
        return 'CLONED'
    else:
        print 'Pulling asset %s' % assetUuid
        command1 = 'pull origin master'
        command2 = 'pull origin master --tags'
        arg1= 'git --work-tree="{d}" --git-dir="{d}/.git" {c}'.format(
            d=asset_folder, c=command1)
        arg2= 'git --work-tree="{d}" --git-dir="{d}/.git" {c}'.format(
            d=asset_folder, c=command2)
        process(arg1)
        process(arg2)
        return 'PULLED'


def getTags(path, assetUuid):
    path = path.encode("utf-8")
    directory = os.path.dirname(path)
    git_dir = os.path.join(GIT_folder, assetUuid)
    command = 'tag -l'
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(
        d=directory, g=git_dir, c=command)
    result, error = process(arg)
    return ','.join(result.strip().split('\n'))


@Capp.task
def identify(path, assetId):
    '''Find video duration'''
    session = Session()
    path = path.encode('utf-8')
    content_type = contenttype(path)
    # if content_type.split('/')[0]=='image':
    #    arg = '''nice identify "%s" 2>&1''' % (path)
    # else:
    arg = '''nice file "%s" 2>&1''' % (path)
    result, error = process(arg)
    if assetId:
        from flib.models import Asset
        target = session.query(Asset).filter_by(id=assetId).first()
        if target and result:
            target.fileinfo = result.replace(path, '').strip()
            session.commit()
    session.close()


@Capp.task
def generateVideoThumbnail(path, assetUuid, version, w=146, h=110, text='thmb'):
    '''generate a thumbnail from a video file and return a vfile db'''
    from flib.models import Asset
    session = Session()
    target = session.query(Asset).filter_by(uuid=assetUuid).first()
    if not target:
        session.close()
        return
    path = path.encode('utf-8')

    fid = target.uuid + '_' + text + '_' + str(version)
    fmt = 'png'
    thpath = os.path.join(public_upload_folder, fid + '.' + fmt)
    arg = '''nice "%s" -i "%s" -an -r 1 -vf "select=gte(n\,10)" -threads 1 -vframes 1 -s %sx%s -y "%s"''' \
        % (ffmpeg, path, w, h, thpath)
    pr = process(arg)
    session.close()
    if os.path.isfile(thpath):
        return thpath


@Capp.task
def generateVideoPreview(path, version, assetUuid):
    '''
        version: asset.version
        asset: asset.uuid
    '''
    path = path.encode('utf-8')
    '''generate a thumbnail from a video file and return a vfile db'''

    fid = assetUuid + '_preview_' + str(version)
    fmt = 'mp4'
    previewPath = os.path.join(public_upload_folder, fid + '.' + fmt)
    '''
        ffmpeg -i movie.mkv -r 30 -strict -2 -async 1 -acodec aac -ac 2 -ab 160k -threads 0 -preset slower -profile:v high -level 4.1 -f mp4 -refs 4 ipadVideo.mp4
    '''

    arg = '''nice "%s" -i "%s" -r 24 -strict -2 -async 1 -acodec aac -ac 2 -ab 160k -threads 1 -preset slower -level 4.1 -f mp4 -refs 4 -s hd480 -y "%s"''' \
        % (ffmpeg, path, previewPath)

    print arg
    pr = process(arg)
    if os.path.isfile(previewPath):
        result = os.path.join('uploads', fid + '.' + fmt)
        return result


@Capp.task
def generateImageThumbnail(path, version, w=146, h=110, asset=None, text='thmb'):
    '''generate thumbnails using convert command'''
    from flib.models import Asset
    session = Session()
    target = session.query(Asset).filter_by(id=asset).first()
    if not target:
        return
    path = path.encode('utf-8')
    content_type = contenttype(path)
    fmt = 'png'
    extra = ''
    page = ''
    # if content_type == 'image/vnd.adobe.photoshop':
    #    extra = '-flatten'
    if content_type == 'application/pdf' or content_type.split('/')[1] in ['gif'] or content_type == 'image/vnd.adobe.photoshop':
        page = '[0]'
    fid = target.uuid + '_' + text + '_' + str(version)
    fmt = 'png'
    newthmbPath = os.path.join(public_upload_folder, fid + '.' + fmt)
    cmd = 'nice convert "%s%s" %s -resize %sx%s "%s"' % (
        path, page, extra, w, h, newthmbPath)
    if content_type == 'image/webp':
        cmd = '%s -i "%s" -s %sx%s "%s"' % (ffmpeg, path, w, h, newthmbPath)
    pr = process(cmd)
    session.close()
    if os.path.isfile(newthmbPath):
        return newthmbPath

        # return os.path.realpath(public_repository_path, previewPath)print
        # task.title


def getTimecode(frame, rate):
    '''Get standard timecode'''
    seconds = frame / rate
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    timecode = "%02d:%02d:%04f" % (h, m, s)
    return timecode


######################################################
######################################################
