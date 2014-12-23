#!../../../pyenv/bin/python
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


import sh
import os
import sys
import base64
import uuid

current_dir = os.path.abspath(os.path.dirname(__file__))
ffmpeg = os.path.join(current_dir, '../../../bin/ffmpeg/ffmpeg')
ffprobe = os.path.join(current_dir, '../../../bin/ffmpeg/ffprobe')

def process(cmd):
    '''General external process'''
    from gevent.subprocess import Popen, PIPE, call  # everything nedded to handle external commands
    p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE,
            )
            #universal_newlines=True)  # process
    (stdout, stderr) = p.communicate()
    return (stdout, stderr)

def duration(path):
    '''Find video duration'''
    arg = '''nice "%s" -show_format "%s" 2>&1''' % (ffprobe, path)
    pr = process(arg)
    dupart = pr[0].split('duration=')  # text processing output of a file
    if pr and len(dupart) > 1:
        du = dupart[1].split()[0]
        try:
            return float(du)
        except ValueError:
            return

def generateThumbnail(path, w=146, h=110, text=None):
    '''generate a thumbnail from a video file and return a vfile db'''
    upf = '/tmp'
    #upf = '/home/farsheed/Desktop'
    fid = uuid.uuid4()
    fmt = 'png'
    thpath = '%s/%s.%s' % (upf, fid, fmt)
    arg = '''nice "%s" -threads 4 -i "%s" -an -r 1 -vf "select=gte(n\,100)" -vframes 1 -s %sx%s -y "%s"''' \
        % (ffmpeg, path, w, h, thpath)
    
    pr = process(arg)
    if os.path.isfile(thpath):
        with open(thpath, 'rb') as newThumb:
            webmode = 'data:image/%s;base64,' % fmt
            return webmode + base64.encodestring(newThumb.read())

        

def getTimecode(frame, rate):
    '''Get standard timecode'''
    seconds = frame / rate
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    timecode = "%02d:%02d:%04f" % (h, m, s)
    return timecode



if __name__ == '__main__':

    print generateThumbnail('/home/farsheed/Raid/Dropbox/Public/datacenter/reel/crash_HDV_v2.mp4')


