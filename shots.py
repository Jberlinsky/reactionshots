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
#import sys
#sys.path.append("/snapchat-python/src/")
from snapchat import Snapchat

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
@app.route("/login", methods=['POST', 'GET'])
def login():
	s = Snapchat()
	s.login(request.form['username'],request.form['password'])
        return Response(json.dumps({"success":s.logged_in}), mimetype='text/javascript')

#send a snapchat
@app.route("/send/<filetype>", methods=['POST'])
def send(filetype):
        app.logger.debug('Starting')
        username = request.form['username']
        password = request.form['password']
        app.logger.warning('2')

	s = Snapchat()
	s.login(username, password)
        app.logger.debug('3')

        app.logger.debug(request.form)
        app.logger.debug(request.files)
        app.logger.debug('4')

        file = request.files['file']
        app.logger.debug('5')
        extension = ".png"
        if filetype == 'video':
                extension = '.mp4'
        filename = 'uploaded_file' + extension

        app.logger.debug('Determined filename ' + filename)

        file.save(filename)

        app.logger.debug('Saved snap')

	#upload file to snapchat
	if (filetype == "image"):
		snapformat = Snapchat.MEDIA_IMAGE
	if (filetype == "video"):
		snapformat = Snapchat.MEDIA_VIDEO
                os.system('rm -rf uploaded_transposed_file.mp4')
                os.system('ffmpeg -i ' + filename + ' -vf "transpose=0" uploaded_transposed_file.mp4')
                filename = 'uploaded_transposed_file.mp4'
                

        app.logger.debug('Preparing to upload')

	media_id = s.upload(snapformat, filename)

        app.logger.debug('Notifying recipient')

	s.send(media_id, request.form['recipient'])

        app.logger.debug('Done!')

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
                        newFile = open('./static/' + snap['id'] + ".jpeg", "wb")
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
                        if fileType == 'image' or fileType == 'video':
                                allsnaps.append({
                                        'file':snap['id'] + ext,
                                        'senderName':snap['sender'],
                                        'fileType': fileType})
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

