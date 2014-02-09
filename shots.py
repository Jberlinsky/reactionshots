"""
SHOTS API for reaction shots (snapchat hack)

requires:
pycrypto==2.6.1
requests==2.0.1

written by Cole Kushner and Jason Berlinsky

"""
import os
from flask import *
import json
import base64
from subprocess import call
from string import split
#import sys
#sys.path.append("/snapchat-python/src/")
from snapchat import Snapchat
import time
from pyres import ResQ

resque = ResQ()

#create our little app
app = Flask(__name__)

import logging
from logging import StreamHandler
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

app.config.from_object(__name__)

@app.route("/")
def begin():
	return "don't be lazy man!\n"

#login verification 
@app.route("/login", methods=['POST'])
def login():
	s = Snapchat()
        username = request.form['username']
        password = request.form['password']
	s.login(username, password)
        resp = 'No'
        if s.logged_in:
                resp = 'Yes'
        return Response(json.dumps([resp]), mimetype='text/javascript')

class SnapContent:
        @staticmethod
        def perform(username, password, filename, filetype, recipients):
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

#send a snapchat
@app.route("/send/<filetype>", methods=['POST'])
def send(filetype):
        username = request.form['username']
        password = request.form['password']
        recipient = request.form['recipient']

        file = request.files['file']
        extension = ".png"
        if filetype == 'video':
                extension = '.mp4'
        filename = username + '_' + str(int(time.time())) + extension

        file.save(filename)

        resque.enqueue(SnapContent, username, password, filename, filetype, recipient)

	return Response(json.dumps({"success":True}), mimetype='text/javascript')
	
#get all snap chats not viewed
@app.route("/getall", methods=['GET'])
def getall():
	#login
	username = request.args.get('username', '')
	password = request.args.get('password', '')
	s = Snapchat()
	s.login(username, password)

	#get all snaps for the user 
	snaps = s.get_snaps()

	allsnaps = []
	for snap in snaps:
                if snap['id'][-1] != 's' and snap['status'] != 2:
                        # Download a snap
                        media = s.get_media(snap['id'])
                        reportedMediaType = snap['media_type']
                        fileType = {
                                None: 'image',
                                1: 'video',
                                2: 'video',
                                3: None,
                                4: None,
                                5: None,
                                6: None
                        }[reportedMediaType]
                        ext = '.mp4'
                        if fileType == 'image':
                                ext = ".jpeg"
                        newFile = open('/var/www/' + snap['id'] + ext, "wb")
                        if fileType == 'image' or fileType == 'video':
                                allsnaps.append({
                                        'file':snap['id'] + ext,
                                        'senderName':snap['sender'],
                                        'fileType': fileType,
                                        'time': snap['time']})
                                newFileByteArray = bytearray(media)
                                newFile.write(newFileByteArray)



	return Response(json.dumps(allsnaps), mimetype='text/javascript')

#get best friends 
@app.route("/getfriends/<amount>", methods=['GET'])
def getbests(amount='all'):
	#login
	username = request.args.get('username', '')
	password = request.args.get('password', '')
	s = Snapchat()
	s.login(username, password)
	if amount == 'all':
			return Response(json.dumps(s.get_updates()['updates_response']['added_friends']), mimetype='text/javascript')
	if amount == 'bests':
			return Response(json.dumps(s.get_updates()['updates_response']['bests']), mimetype='text/javascript')

#clear snapchat history
@app.route("/clear")
def clear():
	s = login()
	s.clear_feed()
	return Response(json.dumps({"success":True}), mimetype='text/javascript') 

if __name__ == "__main__":
    app.run(host='0.0.0.0')

