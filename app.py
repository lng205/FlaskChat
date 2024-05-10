"""
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
"""

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
app.config["SECRET_KEY"] = secrets.token_hex()
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
    return render_template(
        "authenticate.jinja", text="Sign up", url=url_for("signup_user")
    )


@app.route("/login")
def login():
    return render_template(
        "authenticate.jinja", text="Login", url=url_for("login_user")
    )


@app.route("/login/user", methods=["POST"])
def login_user():
    username = request.form.get("username")
    password = request.form.get("password")

    user = db.get_user(username)
    if user is None:
        return jsonify({"error": "User does not exist!"})

    if not bcrypt.checkpw(password.encode(), user.password):
        return jsonify({"error": "Password does not match!"})

    return jsonify(
        {
            "token": create_token(username),
            "username": username,
            "redirect": url_for("message"),
        }
    )


@app.route("/signup/user", methods=["POST"])
def signup_user():
    username = request.form.get("username")
    password = request.form.get("password")

    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode(), salt)

    if db.get_user(username):
        return jsonify({"error": "User already exists!"})

    db.insert_user(username, password)
    return jsonify(
        {
            "token": create_token(username),
            "username": username,
            "redirect": url_for("message"),
        }
    )


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template("404.jinja"), 404


@app.route("/message")
def message():
    username = request.cookies.get("username")
    # token = request.cookies.get("auth_token")
    # if not verify_token(token, username):
    #     abort(401)

    with db.Session(db.engine) as session:
        user = session.get(db.User, username)
        return render_template("message.jinja", user=user)

@app.route("/article", methods=["GET", "POST"])
def article():
    username = request.cookies.get("username")
    # token = request.cookies.get("auth_token")
    # if not verify_token(token, username):
    #     abort(401)

    if request.method == "GET":
        with db.Session(db.engine) as session:
            user = session.get(db.User, username)
            articles = session.scalars(db.select(db.Article))
            return render_template("article.jinja", user=user, articles=articles)
    else:
        # add article
        title = request.json.get("title")
        content = request.json.get("content")
        msg = db.add_article(username, title, content)
        return jsonify({"msg": msg})


@app.route("/comment", methods=["GET", "POST"])
def comment():
    username = request.cookies.get("username")
    # token = request.cookies.get("auth_token")
    # if not verify_token(token, username):
    #     abort(401)

    id = request.args.get("id")
    if request.method == "GET":
        with db.Session(db.engine) as session:
            user = session.get(db.User, username)
            article = session.get(db.Article, id)
            if article is None:
                abort(404)
            return render_template("comment.jinja", user=user, article=article)
    else:
        content = request.json.get("content")
        msg = db.add_comment(username, id, content)
        return jsonify({"msg": msg})


@app.route("/edit", methods=["POST"])
def edit():
    username = request.cookies.get("username")
    # token = request.cookies.get("auth_token")
    # if not verify_token(token, username):
    #     abort(401)

    id = request.json.get("id")
    title = request.json.get("title")
    content = request.json.get("content")
    msg = db.edit_article(username, id, title, content)
    return jsonify({"msg": msg})


@app.route("/delete", methods=["POST"])
def delete():
    username = request.cookies.get("username")
    # token = request.cookies.get("auth_token")
    # if not verify_token(token, username):
    #     abort(401)

    type = request.json.get("type")
    id = request.json.get("id")
    msg = db.delete(username, type, id)
    return jsonify({"msg": msg})


@app.route("/admin", methods=["GET", "POST"])
def admin():
    username = request.cookies.get("username")
    # token = request.cookies.get("auth_token")
    # if not verify_token(token, username) or not db.is_admin(username):
    #     abort(401)

    if request.method == "GET":
        with db.Session(db.engine) as session:
            users = session.scalars(db.select(db.User))
            return render_template("admin.jinja", users=users)
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


if __name__ == "__main__":
    socketio.run(
        app, ssl_context=("ssl/localhost.crt", "ssl/localhost.key"), debug=True
    )
