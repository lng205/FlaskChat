'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, make_response
from flask_socketio import SocketIO
import db
import secrets
import bcrypt
import jwt, datetime

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
    password = request.json.get("password").encode()

    user = db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    stored_hashed_password = user.password
    if not bcrypt.checkpw(password, stored_hashed_password):# 使用检查输入的是否与hash匹配
        return "Error: Password does not match!"

    # Generate token
    token = jwt.encode({
        'user': username,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    # Instead of returning a URL, return a redirect response and set the cookie
    response = make_response(url_for('home', username=username))
    response.set_cookie('auth_token', token, httponly=True, samesite='Lax')

    return response

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

    if db.get_user(username):
        return "Error: User already exists!"

    password_bytes = password.encode()
    salt = bcrypt.gensalt(rounds=12)  # 轮数越大越安全，最大15，但是太大就好慢
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    db.insert_user(username, hashed_password, public_key)

    return url_for('home', username=username)

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token):
        abort(404)
    if request.args.get("username") is None:
        abort(404)
    username = request.args.get("username")
    if db.get_user(username) is None:
        abort(404)
    friends, pending_friends = db.get_friends(username)
    return render_template("home.jinja", username=username, friends=friends, pending_friends=pending_friends)

# Handles a post request when the user clicks the add friend button
@app.route("/home/add", methods=["POST"])
def add_friend():
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token):
        abort(404)
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    friend = request.json.get("friend")

    return db.add_friend(username, friend)

# Handles a post request when the user clicks the accept friend button
@app.route("/home/accept", methods=["POST"])
def process_friend_request():
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token):
        abort(404)
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    friend = request.json.get("friend")
    accept = request.json.get("accept")

    return db.process_friend(username, friend, accept)

@app.route("/home/history", methods=["POST"])
def get_history():
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token):
        abort(404)
    username = request.json.get("username")
    return db.get_history(username)


def verify_token(token):
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return True
    except Exception:
        return False

@app.route("/key")
def get_key():
    username = request.args.get("username")
    return db.get_key(username)

if __name__ == '__main__':
    socketio.run(app, ssl_context=('localhost.crt', 'localhost.key'), debug=True)
