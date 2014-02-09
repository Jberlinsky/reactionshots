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
from tasks import upload_file


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
        filename = username + '_' + recipient + '_' + str(int(time.time())) + extension

        file.save('/tmp/' + filename)

        upload_file.delay(username, password, filename, filetype, recipient)

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
        if snaps == False:
                snaps = []

	allsnaps = []
	for snap in snaps:
                if snap['id'][-1] != 's' and snap['status'] != 2:
                        # Download a snap
                        media = s.get_media(snap['id'])
                        if media == False:
                                s.login(username, password)
                                media = s.get_media(snap['id'])
                                if media == False:
                                        next
                        reportedMediaType = snap['media_type']
                        fileType = {
                                None: 'image',
                                1: 'video',
                                2: 'video',
                                3: None,
                                4: 'image',
                                5: 'video',
                                6: 'video'
                        }[reportedMediaType]
                        ext = '.mp4'
                        if fileType == 'image':
                                ext = ".jpeg"
                        filepath = '/var/www/static/' + username + '_' + snap['id'] + ext
                        os.system('rm -rf ' + filepath)
                        newFile = open(filepath, "wb")
                        if fileType == 'image' or fileType == 'video':
                                newFileByteArray = bytearray(media)
                                if len(newFileByteArray) > 0:
                                        newFile.write(newFileByteArray)
                                        allsnaps.append({
                                                'file':username + '_' + snap['id'] + ext,
                                                'senderName':snap['sender'],
                                                'fileType': fileType,
                                                'time': snap['time']})



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

