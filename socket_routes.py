'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

user_sessions = {}

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id and username:
        join_room(int(room_id))
        emit("incoming", (f"{username} has connected", "green"), to=int(room_id))
        # emit message history
        messages = db.get_messages(room_id)
        for sender, message in messages:
            emit("incoming", (f"{sender}: {message}", "grey"))

    # Map the username to the socket session id
    user_sessions[username] = request.sid

    friends = db.get_friends(username)
    for friend, _ in friends:
        if friend in user_sessions:
            # Notify the user that their friend is online
            emit('status_update', {"username": friend, "online": True}, room=user_sessions[username])
            # Notify the user's friends that the user is online
            emit('status_update', {"username": username, "online": True}, room=user_sessions[friend])

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id and username:
        emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

    # Remove the user from the user_sessions dictionary
    user_sessions.pop(username, None)

    # Notify the user's friends that the user is offline
    friends = db.get_friends(username)
    for friend, _ in friends:
        if friend in user_sessions:
            emit('status_update', {"username": username, "online": False}, room=user_sessions[friend])

# send message event handler
@socketio.on("send")
def send(username, message, room_id):
    emit("incoming", (f"{username}: {message}"), to=room_id)

    # save the message to the database
    db.save_message(username, message, room_id)

# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        # emit message history
        messages = db.get_messages(room_id)
        for sender, message in messages:
            emit("incoming", (f"{sender}: {message}", "grey"))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on("add_friend")
def add_friend(username, friend):
    res = db.add_friend(username, friend)
    emit("add_friend_response", res)
    emit("friend_change", to=user_sessions[friend])

@socketio.on("handle_friend_request")
def handle_friend_request(username, friend, accept):
    db.handle_friend_request(username, friend, accept == "true")
    emit("friend_change")
    emit("friend_change", to=user_sessions[friend])

@socketio.on("remove_friend")
def remove_friend(username, friend):
    db.remove_friend(username, friend)
    emit("friend_change")
    emit("friend_change", to=user_sessions[friend])