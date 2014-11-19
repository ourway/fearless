#!../../pyenv/bin/python
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

import requests
from requests.auth import HTTPBasicAuth
import ujson as json
url = 'http://127.0.0.1:5003/api/sendmail'
data = {}

data['message'] = '''
Hello!, 
This is Farsheed, The developer and designer of Pooyamehr Project|Asset Management System.<br/>
As time passes, tools and features of our software get better and better.  Despite the fact that
I am working on my <a href="http://chista.ir/?p=about">Chista</a> duties to finish ASAP, I
work around the clock to improve and mature our studio's management tools.<br/>

The news is main reporting system is completing and automated reports will be sent to you from time to time.<br/>
Starting Today <b>TUE 18 NOV 2014</b>, the crew will create their profiles and start writing reports based on daily tasks.  
Altough the project management part of the software packege is incomplete, I am trying to integrate management features gradually and carefully to our daily tasks.
<br/>
Based on my schedule, main functionality of the package must be ready within a month.  Thanks for your patience and always happy to hear from you.
<br/>
Have a nice day!

'''

#data['to'] = ['Hamid Lak <hamid2177@gmail.com>', 'Ali Shahdaad <alishahdad1353@yahoo.com>' ]
data['to'] = ['Farsheed Ashouri <farsheed.ashouri@gmail.com>']
data['subject'] = 'A letter to Pooyamehr managers'

r = requests.post(url, data=json.dumps(data), auth=HTTPBasicAuth('rodmena@me.com', 'rrferl'))
print r.reason







