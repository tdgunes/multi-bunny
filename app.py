#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import random
from threading import Thread
from flask import Flask, request, Response, session, stream_with_context, render_template, send_from_directory
from flask.ext.socketio import SocketIO, emit, join_room, leave_room

from uuid import uuid4

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

names = ["Joe", "John", "Small", "B-Bunny", "Jack"]

online_players = {}
speed = 3

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/game')
def test_connect():
	session['id'] = str(uuid4())
	
	name = random.choice(names)+"-"+str(random.randint(1,9999))
	opos = {"x":400, "y":300 ,"name":name, "type":"player", "direction":"right", "id":session['id']}
	emit('identifed', opos ,namespace='/game')
	socketio.emit('newplayer', opos ,namespace='/game')

	for player_name in online_players.keys():
		data = online_players[player_name]
		emit('newplayer', data ,namespace='/game')


	print "Client connected", session["id"], "given name:", name 
	online_players[session['id']] = opos
	#print "added:", name

@socketio.on('disconnect', namespace='/game')
def on_disconnect():
	print "Disconnected", session["id"]
	online_players.pop(session["id"], None)
	socketio.emit("player_disconnected", session["id"], namespace='/game')



@socketio.on('ping', namespace='/game')
def on_ping():
    socketio.emit('pong', None, namespace='/game');
  
@socketio.on('move', namespace='/game')
def move(message):
	if message["type"]=="player":
		player = online_players[message["id"]]

		if message["action"] == "up":
			player["y"] -= speed
			player["direction"] = "up"
		elif message["action"] == "down":
			player["y"] += speed
			player["direction"] = "down"
		elif message["action"] == "left":		
			player["x"] -= speed
			player["direction"] = "left"
		elif message["action"] == "right":		
			player["x"] += speed
			player["direction"] = "right"


		player["x"] = speed if player["x"]<0 else player["x"]
		player["y"] = speed if player["y"]<0 else player["y"]

		socketio.emit('move', player, namespace='/game')
	
	elif message["type"] == "bullet":
		player = online_players[message["name"]]
		print "bullet from ", player 
		socketio.emit('bullet', player, namespace='/game')	

    
    

@app.route('/img/<path:path>')
def static_img_files(path):
    print path
    return send_from_directory('img', path)


@app.route('/css/<path:path>')
def static_font_files(path):
    print path
    return send_from_directory('css', path)


@app.route('/js/<path:path>')
def static_js_files(path):
    print path
    return send_from_directory('js', path)

if __name__ == '__main__':
    
    app.debug = True
    socketio.run(app, host='0.0.0.0')