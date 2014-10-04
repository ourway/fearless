import urllib2
import mmap

# Open the file as a memory mapped string. Looks like a string, but 
# actually accesses the file behind the scenes. 
f = open('video.mkv','rb')
mmapped_file_as_string = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

url = 'http://127.0.0.1:5000/api/asset/save/requests/ipython?name=myvideo.mkv'
# Do the request
request = urllib2.Request(url, mmapped_file_as_string)
request.add_header("Content-Type", "application/zip")
response = urllib2.urlopen(request)

#close everything
mmapped_file_as_string.close()
f.close()
