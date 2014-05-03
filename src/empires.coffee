

WIDTH = 800
HEIGHT = 600

stage = new PIXI.Stage 0xFFFFAA

renderer = PIXI.autoDetectRenderer WIDTH,HEIGHT

document.body.appendChild renderer.view

texture = new PIXI.Texture.fromImage 'img/bunny.png'
background = new PIXI.Texture.fromImage 'img/grass.png'
bullet_texture = new PIXI.Texture.fromImage 'img/bullet.png'

other_players = {}
bullets = {}

namespace = "/game"

my_name = "undefined :) "
socket = io.connect 'http://' + document.domain + ':5000'  + namespace
console.log 'http://' + document.domain + ':5000'  + namespace

background_sprite = new PIXI.Sprite background
stage.addChild background_sprite

main_player = undefined

class Bullet extends PIXI.Sprite
	constructor: (@texture) ->
		super @texture
		@anchor.x = 0.5
		@anchor.y = 0.5


class MainPlayer extends PIXI.Sprite
	constructor: (@texture, @player_name, @c_stage) ->
		super @texture 
		@anchor.x = 0.5
		@anchor.y = 0.5
		@direction = "right"
		@speed = 4
		@r_speed = 0.09
		@r_limit = 0.3
		@position.x = WIDTH / 2
		@position.y = HEIGHT / 2
		@add_title()
		@text.position.y = @position.y - 40
		@text.position.x = @position.x - 25
		@looking = "right"

	add_title: ->
		font = {font:"13.5px Tahoma", fill:"white"}
		@text = new PIXI.Text @player_name, font 
		@c_stage.addChild @text 
		return

	set_player_name:(new_name) ->
		console.log new_name
		@text.setText new_name
		return

	animate: ->
		if @rotation > @r_limit
			@direction = "right"
		else if @rotation < -@r_limit
			@direction = "left"



		@text.position.y = @position.y - 40
		@text.position.x = @position.x - 25

		return

	rotate: ->
		if @direction == "right"
			@rotation -= @r_speed
		else if @direction == "left"
			@rotation += @r_speed
		return 



socket.on 'connect', () ->
	console.log "Connected"
	$("#status").text  "Connected"
	socket.emit 'iamonline', {data: "I'm connected!"}
	return

socket.on 'move', (data) ->
	#console.log 'GOT '+ data.x + " " + data.y
	if data.type == "player"
		player = other_players[data.id]
		player.position.x = data.x
		player.position.y = data.y 
		player.rotate()
	else if data.type == "bullet"
		bullet = bullets[data.id]
		bullet.position.x = data.x
		bullet.position.y = data.y
	return 

setInterval () ->
  startTime = Date.now()
  socket.emit 'ping'
  socket.on 'pong', () ->
    latency = Date.now() - startTime;
    $("#ping").text "Your ping: "+latency+" ms"
    return
  return
 , 750

socket.on 'player_disconnected', (id) ->
	console.log "disconnected_player_id: "+id
	stage.removeChild other_players[id].text
	stage.removeChild other_players[id]
	return 


socket.on 'identifed', (data) ->
	console.log "new player connected " + data.name 
	$("#status").text "identifed " + data.name 
	player =  new MainPlayer texture, data.name ,stage 
	player.position.x = data.x
	player.position.y = data.y
	other_players[data.id] = player
	main_player = data.id
	stage.addChild player
	return

socket.on 'bullet', (data) ->
	bullet = new Bullet bullet_texture
	bullet.position.x = data.x
	bullet.position.y = data.y
	bullets[data.id] = bullet
	stage.addChild bullet
	return 

socket.on 'newplayer', (data) ->
	console.log "new player connected " + data.id 
	$("#status").text "new player connected " + data.id 
	if main_player != data.id
		player =  new MainPlayer texture, data.name ,stage 
		player.position.x = data.x
		player.position.y = data.y
		other_players[data.id] = player
		stage.addChild player

	return 



moveUp = ->
	socket.emit "move",{"action": "up","id":main_player, "type":"player"}
	#console.log "moveUp emitted"
	return
moveDown = ->
	socket.emit "move",{"action": "down", "id":main_player, "type":"player"}
	#console.log "moveDown emitted"
	return
moveLeft = ->
	socket.emit "move",{"action": "left", "id":main_player, "type":"player"}
	#console.log "moveLeft emitted"
	return
moveRight = ->
	socket.emit "move",{"action": "right", "id":main_player, "type":"player"}
	#console.log "moveRight emitted"
	return

sendBullet = ->
	socket.emit "move",{"action": "bullet", "id":main_player, "type":"bullet"}
	#fire here
	return

kd.UP.down moveUp
kd.DOWN.down moveDown
kd.LEFT.down moveLeft
kd.RIGHT.down moveRight
kd.SPACE.down sendBullet


animate = ->
	kd.tick()
	requestAnimFrame animate

	

	for key of other_players
		other_players[key].animate()
	
	
		
	renderer.render stage
	return 

requestAnimFrame animate
return
