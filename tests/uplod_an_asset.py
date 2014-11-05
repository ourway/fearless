#!../pyenv/bin/python

import requests
import ujson as json
import uuid
import os

Api_url = 'http://127.0.0.1/api/asset/save/public?collection=rawfiles&name={name}'

for each in os.listdir('/home/farsheed/Desktop/some_files/A'):
    path = '/home/farsheed/Desktop/some_files/A' + '/' + each
    with  open(path, 'rb') as f:
        r = requests.put(Api_url.format(name=each), data=f)
        res = json.loads(r.content)
        print res.get('url')
