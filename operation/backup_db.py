#!/usr/bin/python

import datetime
import os
import gzip
today = x = datetime.datetime.utcnow()
date = today.strftime('%Y-%m-%d') 
thisdir = os.path.dirname(__file__)
bkname = os.path.abspath(os.path.join(thisdir, 'backups/fearless_db_backup_%s.sql.gz' % date))

bk_command = 'mysqldump -u root -prrferl fearless1 | gzip > %s' % bkname
os.system(bk_command)
data = None
if os.path.isfile(bkname):
    sqlfile = gzip.open(bkname, 'rb')
    data = sqlfile.read()
    data = data.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')

if data:
    sqlfile = gzip.open(bkname, 'wb')
    sqlfile.write(data)
    sqlfile.close()

print 'done! You can import this backup with:\n\tgunzip < %s | mysql -u root -p fearless1' % bkname
        

