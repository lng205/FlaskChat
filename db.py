"""
db
database file, containing all the logic to interface with the sql database
"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database").mkdir(exist_ok=True)

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


def set_account_type(username: str, account_type: str):
    with Session(engine) as session:
        user = session.get(User, username)
        user.account_type = account_type
        session.commit()
        return "Success!"


def add_article(author: str, title: str, content: str):
    with Session(engine) as session:
        article = Article(author=author, title=title, content=content)
        session.add(article)
        session.commit()
        return "Success!"


def edit_article(editor: str, article_id: int, title: str, content: str):
    with Session(engine) as session:
        article = session.get(Article, article_id)
        editor_user_type = session.get(User, editor).account_type
        if article.author != editor and editor_user_type == "student":
            return "Permission Denied!"
        
        article.title = title
        article.content = content
        session.commit()
        return "Success!"


def delete(editor: str, type: str, data_id: int):
    with Session(engine) as session:
        editor_user_type = session.get(User, editor).account_type
        if editor_user_type == "student":
            return "Permission Denied!"
        
        if type == "article":
            data = session.get(Article, data_id)
        else:
            data = session.get(Comment, data_id)            
        session.delete(data)
        session.commit()
        return "Success!"


def add_comment(author: str, article_id: int, content: str):
    with Session(engine) as session:
        comment = Comment(article_id=article_id, author=author, content=content)
        session.add(comment)
        session.commit()
        return "Success!"