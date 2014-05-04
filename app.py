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
bullets = []
speed = 4
bullet_speed = 0.01

WIDTH = 800
HEIGHT = 600

def move_bullets():
	print "Bullet thread, activated..."
	while True:
		time.sleep(bullet_speed)
		for bullet in bullets:
			
			if bullet["direction"] == "right":
				bullet["x"] += speed + 4
			elif bullet["direction"] == "left":
				bullet["x"] -= speed + 4
			elif bullet["direction"] == "up":
				bullet["y"] -= speed + 4
			elif bullet["direction"] == "down":
				bullet["y"] += speed + 4

			if  bullet["x"] < 0 or bullet["x"] > WIDTH or \
			 bullet["y"] < 0 or bullet["y"] > HEIGHT:
			 	socketio.emit('bullet-remove', bullet, namespace='/game')
				bullets.remove(bullet)

			socketio.emit('bullet-move', bullet, namespace='/game')



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

		player["x"] = WIDTH-speed if player["x"]>WIDTH else player["x"]
		player["y"] = HEIGHT-speed if player["y"]>HEIGHT else player["y"]

		socketio.emit('move', player, namespace='/game')

@socketio.on('new_bullet', namespace='/game')
def on_new_bullet(data):
	sender = online_players[data["id"]]
	bullet = {}
	bullet["x"] = sender["x"]
	bullet["direction"] = sender["direction"]
	bullet["y"] = sender["y"]
	bullet["id"] =str(uuid4())
	bullets.append(bullet)
	socketio.emit('bullet', bullet , namespace='/game')	

    

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
    Thread(target=move_bullets).start()
    app.debug = True
    socketio.run(app, host='0.0.0.0')