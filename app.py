'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, jsonify
from flask_socketio import SocketIO
import db
import secrets
import bcrypt
import jwt
import datetime

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

CSP = "default-src 'self'; script-src 'self';"

@app.after_request
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = CSP
    return response

@app.route("/")
def index():
    return render_template("index.jinja")

@app.route("/signup")
def signup():
    return render_template("authenticate.jinja", text="Sign up", url=url_for("signup_user"))

@app.route("/login")
def login():    
    return render_template("authenticate.jinja", text="Login", url=url_for("login_user"))

@app.route("/login/user", methods=["POST"])
def login_user():
    username = request.form.get("username")
    password = request.form.get("password")

    user =  db.get_user(username)
    if user is None:
        return jsonify({"error": "User does not exist!"})

    if not bcrypt.checkpw(password.encode(), user.password):
        return jsonify({"error": "Password does not match!"})

    return jsonify({
        "token": create_token(username),
        "username": username,
        "redirect": url_for("home", username=username)
        })

@app.route("/signup/user", methods=["POST"])
def signup_user():
    username = request.form.get("username")
    password = request.form.get("password")

    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode(), salt)

    if db.get_user(username):
        return jsonify({"error": "User already exists!"})

    db.insert_user(username, password)
    return jsonify({
        "token": create_token(username),
        "username": username,
        "redirect": url_for("home", username=username)
        })

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    # User can OLNY access their own home page
    username = request.args.get("username")
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token, username):
        abort(401)

    return render_template(
        "home.jinja",
        username=username,
        friends=db.get_friends(username),
        pending_friends=db.get_pending_friends(username),
    )

# handler of friend requests
@app.route("/home/add", methods=["POST"])
def add_friend():
    username = request.cookies.get('username')
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token, username):
        abort(401)

    friend = request.form.get("friend")
    res = db.add_friend(username, friend)
    return jsonify({"message": res}), 200

# handler of processing friend requests
@app.route("/home/process", methods=["POST"])
def process_friend_request():
    username = request.cookies.get("username")
    token = request.cookies.get('auth_token')
    if token is None or not verify_token(token, username):
        abort(401)

    friend = request.json.get("friend")
    accept = request.json.get("accept")

    return db.process_friend_request(username, friend, accept)


def create_token(username):
    return jwt.encode(
        {
            "user": username,
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )

def verify_token(token, username):
    try:
        return (
            username
            == jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])["user"]
        )
    except Exception:
        return False

if __name__ == '__main__':
    socketio.run(app, ssl_context=('ssl/localhost.crt', 'ssl/localhost.key'), debug=True)
