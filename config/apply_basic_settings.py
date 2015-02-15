#!../pyenv/bin/python

import sys, os
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/api'))
sys.path.append(module_path)


from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy.orm import subqueryload
from models import *
from mako.template import Template
import copy


user1 = User(email='farsheed.ashouri@gmail.com', password='rrferl', active=True, firstname='Farsheed', lastname='Ashouri')
user2 = User(email='mehdieyazdani@gmail.com', password='123456', active=True, firstname='Mehdi', lastname='Yazdani')
user3 = User(email='mostafarayaneh@gmail.com', password='123456', active=True, firstname='Morteza', lastname='Gaamari')
user4 = User(email='amirgholamzadeh@gmail.com', password='123456', active=True, firstname='Amir', lastname='Gholam Zadeh')
user5 = User(email='mostafa_khaleghi64@yahoo.com', password='123456', active=True, firstname='Mostafa', lastname='Khalegi')
user6 = User(email='hamedanime@gmail.com', password='123456', active=True, firstname='Hamed', lastname='Behroozi')
user7 = User(email='shahriyar.shahramfar@gmail.com', password='123456', active=True, firstname='Bijan', lastname='Shahramfar')
user8 = User(email='mhd.kheirandish@yahoo.com', password='123456', active=True, firstname='Mohammad', lastname='Kheirandish')
user9 = User(email='mehrdadshahverdi81@gmail.com', password='123456', active=True, firstname='Mehrdad', lastname='Shahverdi')
user10 = User(email='firoozeh.imany@gmail.com', password='123456', active=True, firstname='Firoozeh', lastname='Imani')
user11 = User(email='parima.1367@yahoo.com', password='123456', active=True, firstname='Parima', lastname='Daliri')
user12 = User(email='mina.nazaralhooee@gmail.com', password='123456', active=True, firstname='Mina', lastname='Nazari')
user13 = User(email='arashentezami3d@gmail.com', password='123456', active=True, firstname='Arash', lastname='Entezami')
user14 = User(email='zara.erfani@yahoo.com', password='123456', active=True, firstname='Zahra', lastname='Erfani')
user15 = User(email='negarahmadi13@gmail.com', password='123456', active=True, firstname='Negar', lastname='Ahmadi')
user16 = User(email='merfanparsapour@yahoo.com', password='123456', active=True, firstname='Erfan', lastname='Parsapour')
user17 = User(email='f.shamayel@gmail.com', password='123456', active=True, firstname='Farshad', lastname='Shamayel')
user18 = User(email='amin.zarouni@gmail.com', password='123456', active=True, firstname='Amin', lastname='Zarouni')
user19 = User(email='khalil66@gmail.com', password='123456', active=True, firstname='Khalil', lastname='Khaliliyan')
user20 = User(email='hamid2177@gmail.com', password='123456', active=True, firstname='Hamid', lastname='Lak')
user21 = User(email='mepayam@gmail.com', password='123456', active=True, firstname='Payam', lastname='Memar')
user22 = User(email='alishahdad1353@yahoo.com', password='123456', active=True, firstname='Ali', lastname='Shahdad')
user23 = User(email='hamid_sohrabi_vale@yahoo.com', password='123456', active=True, firstname='Hamid', lastname='Sohrabi')
user24 = User(email='rangekhod.2000@yahoo.com', password='123456', active=True, firstname='Majid', lastname='Majidi')
user25 = User(email='banomo1982@yahoo.com', password='123456', active=True, firstname='Bahare', lastname='Mogaddam')
user26 = User(email='amirhoseinkasraee@yahoo.com', password='123456', active=True, firstname='AmirHossein', lastname='Kasrayi')
user27 = User(email='nsns_1300@yahoo.com', password='123456', active=True, firstname='Nasim', lastname='Sadegi')
user28 = User(email='zahra.mansouriyeh@gmail.com', password='123456', active=True, firstname='Zahra', lastname='Mansooriye')
user29 = User(email='alenhue@gmail.com', password='123456', active=True, firstname='Arash', lastname='Mogaddam')
user30 = User(email='sara_kayvan@hotmail.com', password='123456', active=True, firstname='Sara', lastname='Keyvan')
user31 = User(email='bitarafali@yahoo.com', password='123456', active=True, firstname='Ali', lastname='Bitaraf')
user32 = User(email='mj.hagh@gmail.com', password='123456', active=True, firstname='Majid', lastname='Hagighighatjoo')
user33 = User(firstname="Amir", lastname="Mohammad", email="amirm5831@gmail.com", password="123456", active=True)
user34 = User(firstname="Sadegh", lastname="Hosseini", email="Sadegh131313@yahoo.com", password="123456", active=True)



from models.db import Session
session = Session()


session.add_all([ user1, user2, user3, user4, user5, user6, user7, user8, user9,
                 user10, user11, user12, user13, user14, user15, user16, user17,
                 user18, user19, user20, user21, user22, user23, user24, user25,
                 user26, user27, user28, user29, user30, user31, user32, 
                 user33, user34])
user1.groups.append('admin')
session.commit()
    #import shutil
#print animate.get_tree(session, json=True)

#proj.plan



session.close()

    #print maya_section.assets
    #shutil.copyfileobj(maya_section.archive, open('maya_section.tar', 'w'))

