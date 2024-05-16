"""
socket_routes
file containing all the routes related to socket.io
"""

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
@socketio.on("connect")
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id and username:
        join_room(int(room_id))
        emit("incoming", (f"{username} has connected", "green"), to=int(room_id))
        # emit message history
        with db.Session(db.engine) as session:
            messages = session.scalars(
                db.select(db.Message).where(db.Message.room_id == room_id)
            )
            for message in messages:
                emit("incoming", (f"{message.sender}: {message.message}", "grey"))

    # Map the username to the socket session id
    user_sessions[username] = request.sid

    with db.Session(db.engine) as session:
        user = session.get(db.User, username)
        for friend in user.friends:
            if friend.username in user_sessions:
                emit(
                    "status_update",
                    {"username": friend.username, "online": True},
                    to=user_sessions[user.username],
                )
                emit(
                    "status_update",
                    {"username": user.username, "online": True},
                    to=user_sessions[friend.username],
                )


# event when client disconnects
# quite unreliable use sparingly
@socketio.on("disconnect")
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id and username:
        emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

    # Remove the user from the user_sessions dictionary
    user_sessions.pop(username, None)

    # Notify the user's friends that the user is offline
    with db.Session(db.engine) as session:
        user = session.get(db.User, username)
        for friend in user.friends:
            if friend.username in user_sessions:
                emit(
                    "status_update",
                    {"username": user.username, "online": False},
                    to=user_sessions[friend.username],
                )


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

    # Get the pair's room id
    room_id = db.get_room_id(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id)

    with db.Session(db.engine) as session:
        messages = session.scalars(
            db.select(db.Message).where(db.Message.room_id == room_id)
        )
        for message in messages:
            emit("incoming", (f"{message.sender}: {message.message}", "grey"))
    
    return room_id


@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)


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
