from snapchat import Snapchat
import time
import os
from string import *
from celery import Celery

from celery.utils.log import get_task_logger

bg = Celery('tasks', broker='amqp://guest@localhost//')
logger = get_task_logger(__name__)
@bg.task
def upload_file(username, password, filename, filetype, recipients):
        s = Snapchat()
        s.login(username, password)
        #upload file to snapchat
        if (filetype == "image"):
                snapformat = Snapchat.MEDIA_IMAGE
        if (filetype == "video"):
                snapformat = Snapchat.MEDIA_VIDEO
                print "Setting up new filename"
                new_filename = replace(filename, '.mp4', '_transposed.mp4')
                print "New filename: " + filename
                os.system('rm -rf ' + new_filename)
                print "Empty location"
                os.system('ffmpeg -i ' + filename + ' -vf "transpose=0" ' + new_filename)
                print "TRANSPOSED!"
                filename = new_filename
        media_id = s.upload(snapformat, filename)
        return s.send(media_id, split(recipients, ','), 5)
