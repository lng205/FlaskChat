'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

def get_friends(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        if user is None:
            return []
        return [friend.username for friend in user.friends]

def get_pending_friends(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        if user is None:
            return []
        return [friend.username for friend in user.pending_friends]
    
def add_friend(username: str, friendname: str):
    with Session(engine) as session:
        user = session.get(User, username)
        friend = session.get(User, friendname)
        if friend is None or user is None:
            return "User does not exist!"
        if friend in user.friends:
            return "User already a friend!"
        if friend == user:
            return "Cannot add yourself as a friend!"
        if user in friend.pending_friends:
            return "Friend request already sent!"
        friend.pending_friends.append(user)
        session.commit()
        return "Success!"

def handle_friend_request(username: str, friendname: str, accept: bool):
    with Session(engine) as session:
        user = session.get(User, username)
        friend = session.get(User, friendname)
        user.pending_friends.remove(friend)
        if accept:
            user.friends.append(friend)
            friend.friends.append(user)
        session.commit()

def remove_friend(username: str, friendname: str):
    with Session(engine) as session:
        user = session.get(User, username)
        friend = session.get(User, friendname)
        user.friends.remove(friend)
        friend.friends.remove(user)
        session.commit()

def save_message(sender: str, message: str, room_id: int):
    with Session(engine) as session:
        message = Message(sender=sender, message=message, room_id=room_id)
        session.add(message)
        session.commit()

def get_messages(room_id: int):
    with Session(engine) as session:
        messages = session.scalars(select(Message).where(Message.room_id == room_id))
        return [(message.sender, message.message) for message in messages]