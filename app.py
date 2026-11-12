from flask import Flask
from flask import redirect, render_template, request, session, flash, abort
import secrets
import config
import sqlite3
import users
import decks

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_decks = decks.get_decks()
    return render_template("index.html", decks=all_decks)

@app.route("/new_deck")
def new_deck():
    require_login()
    return render_template("new_deck.html")

@app.route("/create_deck", methods=["POST"])
def create_deck():
    require_login()
    check_csrf()

    name = request.form["name"]
    if not name or len(name) > 50:
        abort(403)

    description = request.form["description"]
    if len(description) > 1000:
        abort(403)

    user_id = session["user_id"]

    deck_id = decks.add_deck(name, description, user_id)
    return redirect("/deck/" + str(deck_id))

@app.route("/deck/<int:deck_id>")
def show_deck(deck_id):
    deck = decks.get_deck(deck_id)
    if not deck:
        abort(404)

    cards = decks.get_cards(deck_id)

    return render_template("show_deck.html", deck=deck, cards=cards)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("Error: Passwords dont match")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("Error: User already exists")
        return redirect("/register")

    flash("Account created succesfully!")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("Error: Wrong username or password")
            return redirect("/login")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
        del session["csrf_token"]
    return redirect("/")