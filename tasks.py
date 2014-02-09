from snapchat import Snapchat
import time
import os
from string import *
from celery import Celery
from pymongo import MongoClient
import datetime

Mongo = MongoClient('localhost', 27017)
MongoDB = Mongo.snap
Connections = MongoDB.connections

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
        elif (filetype == "video"):
                snapformat = Snapchat.MEDIA_VIDEO
                new_filename = replace(filename, '.mp4', '_transposed.mp4')
                os.system('rm -rf ' + new_filename)
                os.system('ffmpeg -i ' + filename + ' -vf "transpose=0" ' + new_filename)
                filename = new_filename
        else:
                return
        media_id = s.upload(snapformat, filename)
        all_recipients = split(recipients, ',')
        s.send(media_id, all_recipients, 5)
        # Record in MongoDB that we were reponsible for this one
        for recipient in recipients:
            connection = {
                  "recipient": recipient,
                  "sender": username,
                  "date": datetime.datetime.utcnow(),
                  "id": media_id
            }
            Connections.insert(connection)
