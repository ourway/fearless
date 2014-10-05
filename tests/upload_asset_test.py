

import requests

files = {'asset':open('video.mkv', 'rb')}
data = open('video.mkv', 'rb')
url = 'http://127.0.0.1:5005/utils/asset/fereydoon/images/video2.mkv'

requests.post(url, data=data)

