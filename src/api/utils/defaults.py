__author__ = 'farsheed'
import os
import user

fearless_folder = os.path.abspath(os.path.dirname(__file__))
public_repository_path = os.path.join(user.home, '.fearlessrepo')









#####################################
for i in [public_repository_path]:
    if not os.path.isdir(i):
        os.makedirs(i)
#####################################
