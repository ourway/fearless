

import os
FFMPEG = '/home/farsheed/Documents/dev/fa-team/bin/ffmpeg/ffmpeg'



def getExt(filename):
    return filename.split('.')[-1]

def convert(path, exts=['avi', 'mov']):
    for root, dirs, files in os.walk(path):
        for name in files:
            filepath = os.path.abspath(os.path.join(root, name))
            if  getExt(filepath) and getExt(filepath).lower() in exts:
                print 'converting %s' % filepath
                newfile = filepath + '.m4v'
                cmd = '{ffmpeg} -i "{path}" -y -threads 8 "{output}"'.format(ffmpeg=FFMPEG, path=filepath,
                                                        output = newfile)
                os.system(cmd)
                os.remove(filepath)
                print newfile
 



if __name__ == '__main__':
    convert('/home/farsheed/windows_share/model_assets')
