'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
import db
import secrets

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if user.password != password:
        return "Error: Password does not match!"

    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")
    public_key = request.json.get("publicKey")

    if db.get_user(username) is None:
        db.insert_user(username, password, public_key)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    username = request.args.get("username")
    if username is None:
        abort(404)
    friends, pending_friends = db.get_friends(username)
    return render_template(
        "home.jinja",
        username=username,
        friends=friends,
        pending_friends=pending_friends,
    )

# handler of friend requests
@app.route("/home/add", methods=["POST"])
def add_friend():
    username = request.json.get("username")
    friend = request.json.get("friend")
    return db.add_friend(username, friend)

# handler of processing friend requests
@app.route("/home/process", methods=["POST"])
def process_friend_request():
    username = request.json.get("username")
    friend = request.json.get("friend")
    accept = request.json.get("accept")
    return db.process_friend_request(username, friend, accept)

@app.route("/key")
def get_key():
    return db.get_key(request.args.get("keyof"))

if __name__ == '__main__':
    socketio.run(app)
