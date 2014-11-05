__author__ = 'farsheed'
import os
fearless_folder = os.path.abspath(os.path.dirname(__file__))
public_repository_path = os.path.abspath(os.path.join(fearless_folder, '../../../REPOSITORIES'))









#####################################
for i in [public_repository_path]:
    if not os.path.isdir(i):
        os.makedirs(i)
#####################################