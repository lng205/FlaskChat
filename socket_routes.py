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

import db

user_sessions: dict[str, int] = {}


class RoomMembers:
    def __init__(self):
        self.room_members: dict[str, set[str]] = {}

    def add_member(self, room_id: str, username: str):
        if room_id not in self.room_members:
            self.room_members[room_id] = set()
        self.room_members[room_id].add(username)

    def remove_member(self, room_id: str, username: str):
        if room_id in self.room_members:
            self.room_members[room_id].remove(username)

    def print_room_members(self, room_id: str) -> str:
        if room_id in self.room_members:
            return " ".join(map(str, self.room_members[room_id]))
        return ""


room_members = RoomMembers()


# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on("connect")
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id and username:
        join_room_wrapper(username, room_id)

    for friend in db.get_friends(username):
        if friend in user_sessions:
            emit("status_update", {"username": friend, "online": True})
            emit(
                "status_update",
                {"username": username, "online": True},
                to=user_sessions[friend],
            )

    user_sessions[username] = request.sid


# event when client disconnects
# quite unreliable use sparingly
@socketio.on("disconnect")
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id and username:
        emit("incoming", (f"{username} has disconnected", "red"), to=room_id)

    # Remove the user from the user_sessions dictionary
    user_sessions.pop(username, None)

    for friend in db.get_friends(username):
        if friend in user_sessions:
            emit(
                "status_update",
                {"username": username, "online": False},
                to=user_sessions[friend],
            )


# send message event handler
@socketio.on("send")
def send(username, message, room_id):
    emit("incoming", (f"{username}: {message}"), to=room_id)
    db.save_message(username, message, room_id)


@socketio.on("private_chat")
def private_chat(sender_name, receiver_name):
    room_id = db.get_private_chat_room(sender_name, receiver_name)
    join_room_wrapper(sender_name, room_id)
    return room_id


@socketio.on("join_room")
def join_chat_room(username, room_id):
    if db.get_room_receiver(room_id, username) is not None:
        return "This is a private chat room."
    if db.room_exists(room_id):
        join_room_wrapper(username, room_id)
        return "Success!"
    return "Room does not exist."


@socketio.on("create_room")
def create_room(username):
    room_id = db.create_room()
    join_room_wrapper(username, room_id)
    return room_id


@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    room_members.remove_member(room_id, username)
    emit("room_member_change", room_members.print_room_members(room_id), to=room_id)
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


def join_room_wrapper(username, room_id):
    join_room(room_id)
    receiver = db.get_room_receiver(room_id, username)
    if receiver is not None:
        # Private chat
        emit(
            "incoming",
            (f"{username} has started chatting with {receiver}.", "green"),
            to=room_id,
        )
    else:
        # Public chat
        emit(
            "incoming",
            (f"{username} has joined the room {room_id}.", "green"),
            to=room_id,
        )

        # Emit all users in the room
        room_members.add_member(room_id, username)
        emit("room_member_change", room_members.print_room_members(room_id), to=room_id)

    # History
    for sender, message in db.get_messages(room_id):
        emit("incoming", (f"{sender}: {message}", "grey"))
