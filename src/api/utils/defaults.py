__author__ = 'farsheed'
import os
import user
home = user.home
fearless_folder = os.path.abspath(os.path.dirname(__file__))
public_repository_path = os.path.join(home, '.fearlessrepo')
public_upload_folder = os.path.join(home, '.fearlessrepo/uploads')
GIT_folder = os.path.join(home, '.fearlessrepo/GIT')
ASSETS = os.path.join(home, '.fearlessrepo/ASSETS')









#####################################
for i in [public_repository_path, public_upload_folder, GIT_folder, ASSETS]:
    if not os.path.isdir(i):
        os.makedirs(i)
#####################################
