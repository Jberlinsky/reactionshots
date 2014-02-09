from snapchat import Snapchat
import time
import os
import string
from celery import Celery

bg = Celery('tasks', broker='redis://localhost', backend='redis://localhost')
@bg.task
def upload_file(username, password, filename, filetype, recipients):
        print "GOT HERE"
        s = Snapchat()
        s.login(username, password)
        print "Parsing"
        #upload file to snapchat
        if (filetype == "image"):
                snapformat = Snapchat.MEDIA_IMAGE
        if (filetype == "video"):
                snapformat = Snapchat.MEDIA_VIDEO
                new_filename = replace(filename, '.mp4', '_transposed.mp4')
                os.system('rm -rf ' + new_filename)
                os.system('ffmpeg -i ' + filename + ' -vf "transpose=0" ' + new_filename)
                filename = new_filename
        print "Sending..."

        media_id = s.upload(snapformat, filename)

        s.send(media_id, split(recipients, ','), 5)

