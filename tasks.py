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
        logger.debug("GOT HERE")
        s = Snapchat()
        s.login(username, password)
        logger.debug('Parsing')
        #upload file to snapchat
        if (filetype == "image"):
                snapformat = Snapchat.MEDIA_IMAGE
        if (filetype == "video"):
                snapformat = Snapchat.MEDIA_VIDEO
                new_filename = replace(filename, '.mp4', '_transposed.mp4')
                os.system('rm -rf ' + new_filename)
                os.system('ffmpeg -i ' + filename + ' -vf "transpose=0" ' + new_filename)
                filename = new_filename
        logger.debug("Sending...")

        media_id = s.upload(snapformat, filename)

        logger.debug("Notifying")

        s.send(media_id, split(recipients, ','), 5)
        logger.debug("DONE")
