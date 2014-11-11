__author__ = 'farsheed'
import os
fearless_folder = os.path.abspath(os.path.dirname(__file__))
public_repository_path = os.path.join(os.getenv('HOME'), '.fearlessrepo')









#####################################
for i in [public_repository_path]:
    if not os.path.isdir(i):
        os.makedirs(i)
#####################################
