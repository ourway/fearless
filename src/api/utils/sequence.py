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


import falcon
import ujson
import hashlib
from helpers import commit, get_ip, get_params
from models import Sequence, Shot, session, Project, User

class AddSequence:
    @falcon.after(commit)
    def on_put(self, req, resp, projId):
        targetProject = session.query(Project).filter(Project.id==int(projId)).first()
        form = get_params(req.stream, flat=False)
        if targetProject and form.get('number') and form.get('lead'):
            lead = session.query(User).filter(User.id == int(form.get('lead').get('id'))).first()
            lenOfSeqs = len(targetProject.sequences)
            if lead:
                number = int(form.get('number'))
                if number > 0:  ## now its ok to add sequences
                    for newSeq in xrange(number):
                        num = lenOfSeqs + 1
                        new = Sequence(number=num)
                        targetProject.sequences.append(new)
                        lenOfSeqs += 1

                    ##
                    count = 1
                    for seq in targetProject.sequences:
                        seq.number = count
                        count +=1
                    
                    
                    resp.status = falcon.HTTP_202
                    resp.body = {'message':'OK'}

                        





