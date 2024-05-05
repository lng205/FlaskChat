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
        "redirect": url_for("message")
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
        "redirect": url_for("message")
        })

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

@app.route("/message")
def message():
    token = request.cookies.get('auth_token')
    username = request.cookies.get("username")
    if not verify_token(token, username):
        abort(401)

    return render_template(
        "message.jinja",
        username=username,
        account_type=db.get_account_type(username),
        friends=db.get_friends(username),
        pending_friends=db.get_pending_friends(username),
    )

@app.route("/article", methods=["GET", "POST"])
def article():
    username = request.cookies.get("username")
    if request.method == "GET":
        return render_template(
            "article.jinja",
            username=username,
            account_type=db.get_account_type(username)
        )
    else:
        msg = db.add_article(username, request.json.get("text"))
        return jsonify({"msg": msg})

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        token = request.cookies.get('auth_token')
        username = request.cookies.get("username")
        if not verify_token(token, username) or not db.is_admin(username):
            abort(401)
        return render_template("admin.jinja", userdata=db.get_all_users())
    else:
        username = request.json.get("username")
        account_type = request.json.get("type")
        msg = db.set_account_type(username, account_type)
        return jsonify({"msg": msg})

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
