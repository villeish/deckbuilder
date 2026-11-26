from flask import Flask
from flask import redirect, render_template, request, session, flash, abort
import secrets
import config
import sqlite3
import users
import decks
import comments as comments_db

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
    all_tags = decks.get_tags()
    return render_template("index.html", decks=all_decks, all_tags=all_tags)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)

    if not user:
        abort(404)

    all_decks = users.get_decks(user_id)
    stats = users.get_user_stats(user_id)

    return render_template("show_user.html", user=user, decks=all_decks, stats=stats)

@app.route("/search")
def search():
    query = request.args.get("query", "")

    tag_ids = request.args.getlist("tags")
    results = decks.find_decks(query, tag_ids)
    all_tags = decks.get_tags()
    return render_template("index.html", decks=results, all_tags=all_tags)

@app.route("/new_deck")
def new_deck():
    require_login()
    all_tags = decks.get_tags()
    return render_template("new_deck.html", all_tags=all_tags, name="", description="", selected_tags=[])

@app.route("/create_deck", methods = ["POST"])
def create_deck():
    require_login()
    check_csrf()

    name = request.form["name"].strip()
    description = request.form["description"].strip()
    tag_ids = request.form.getlist("tags")

    all_tags = decks.get_tags()
    valid_tag_ids = [str(tag["id"]) for tag in all_tags]

    errors = []

    if not name or len(name) > 50:
        errors.append("Deck name must be between 1-50 characters!")

    if len(description) > 1000:
        errors.append("Deck description is too long!")

    for tag_id in tag_ids:
        if tag_id not in valid_tag_ids:
            errors.append("Invalid tag selection!")
            break

    if errors:
        for error in errors:
            flash(error)
        return render_template("new_deck.html", all_tags=all_tags, name=name, description=description, selected_tags=tag_ids)

    user_id = session["user_id"]
    deck_id = decks.add_deck(name, description, user_id)

    for tag_id in tag_ids:
        decks.add_deck_tag(deck_id, int(tag_id))

    return redirect("/deck/" + str(deck_id))

@app.route("/deck/<int:deck_id>")
def show_deck(deck_id):
    deck = decks.get_deck(deck_id)
    if not deck:
        abort(404)

    cards = decks.get_cards(deck_id)
    tags = decks.get_deck_tags(deck_id)
    comments = comments_db.get_comments(deck_id)

    return render_template("show_deck.html", deck=deck, cards=cards, tags=tags, comments=comments)

@app.route("/edit_deck/<int:deck_id>", methods=["GET", "POST"])
def edit_deck(deck_id):
    require_login()

    deck = decks.get_deck(deck_id)

    if not deck:
        abort(404)

    if deck["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        all_tags = decks.get_tags()
        deck_tags = decks.get_deck_tags(deck_id)
        selected_tag_ids = [tag["id"] for tag in deck_tags]
        return render_template("edit_deck.html", deck=deck, name=deck["name"], description=deck["description"], all_tags=all_tags, selected_tag_ids=selected_tag_ids)

    check_csrf()

    name = request.form["name"].strip()
    description = request.form["description"].strip()
    tag_ids = request.form.getlist("tags")

    errors = []

    if name == "":
        errors.append("You must give the deck a name!")

    if len(name) > 50:
        errors.append("Deck name is too long!")

    if len(description) > 1000:
        errors.append("Deck description is too long!")

    all_tags = decks.get_tags()
    valid_tag_ids = [str(tag["id"]) for tag in all_tags]

    if any(tag_id not in valid_tag_ids for tag_id in tag_ids):
        errors.append("Invalid tag selection!")

    if errors:
        for error in errors:
            flash(error)
        return render_template("edit_deck.html", deck=deck, name=name, description=description, all_tags=all_tags, selected_tag_ids=[int(tag_id) for tag_id in tag_ids if tag_id in valid_tag_ids])

    decks.update_deck(deck_id, name, description)
    decks.remove_deck_tags(deck_id)

    for tag_id in tag_ids:
        decks.add_deck_tag(deck_id, int(tag_id))

    flash("Deck details updated.")
    return redirect("/deck/" + str(deck_id))

@app.route("/remove_deck/<int:deck_id>", methods=["GET", "POST"])
def remove_deck(deck_id):
    require_login()

    deck = decks.get_deck(deck_id)

    if not deck:
        abort(404)

    if deck["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "POST":
        check_csrf()

        if "remove" in request.form:
            decks.remove_deck(deck_id)
            return redirect("/")
        else:
            return redirect("/deck/" + str(deck_id))

    return render_template("remove_deck.html", deck=deck)

@app.route("/edit_cards/<int:deck_id>")
def edit_cards(deck_id):
    require_login()

    deck = decks.get_deck(deck_id)

    if not deck:
        abort(404)

    if deck["user_id"] != session["user_id"]:
        abort(403)

    cards = decks.get_cards(deck_id)

    return render_template("edit_cards.html", deck=deck, cards=cards)

@app.route("/add_card", methods=["POST"])
def add_card():
    require_login()
    check_csrf()

    deck_id = request.form["deck_id"]
    card_name = request.form["card_name"].strip()
    quantity = request.form["quantity"]

    errors = []

    if not deck_id.isdigit():
        abort(403)

    if not card_name or len(card_name) > 100:
        errors.append("Card name must be between 1 and 100 characters!")

    if not quantity.isdigit() or int(quantity) < 1 or int(quantity) > 99:
        errors.append("Card quantity must be between 1 and 99!")

    deck_id = int(deck_id)
    deck = decks.get_deck(deck_id)

    if not deck:
        abort(404)

    if deck["user_id"] != session["user_id"]:
        abort(403)

    if errors:
        for error in errors:
            flash(error)
        cards = decks.get_cards(deck_id)
        return render_template("edit_cards.html", deck=deck, cards=cards, new_card_name=card_name, new_quantity=quantity)

    if not decks.add_card(deck_id, card_name, int(quantity)):
        flash("A deck cannot contain more than 99 copies of a card.")
        cards = decks.get_cards(deck_id)
        return render_template("edit_cards.html", deck=deck, cards=cards, new_card_name=card_name, new_quantity=quantity)

    return redirect("/edit_cards/" + str(deck_id))

@app.route("/update_card", methods=["POST"])
def update_card():
    require_login()
    check_csrf()

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]

    if not deck_id.isdigit() or not card_id.isdigit():
        abort(403)

    deck_id = int(deck_id)
    card_id = int(card_id)

    deck = decks.get_deck(deck_id)
    if not deck:
        abort(404)

    if deck["user_id"] != session["user_id"]:
        abort(403)

    cards = decks.get_cards(deck_id)
    if not any(card["id"] == card_id for card in cards):
        abort(404)

    card_name = request.form["card_name"]
    quantity = request.form["quantity"]

    errors = []

    if not card_name or len(card_name) > 100:
        errors.append("Card name must be between 1 and 100 characters!")

    if not quantity.isdigit() or int(quantity) < 1 or int(quantity) > 99:
        errors.append("Card quantity must be between 1 and 99!")

    if errors:
        for error in errors:
            flash(error)
        return render_template("edit_cards.html", deck=deck, cards=cards, edited_card_id=card_id, edited_card_name=card_name, edited_quantity=quantity)

    decks.update_card(card_id, card_name, int(quantity))

    return redirect("/edit_cards/" + str(deck_id))

@app.route("/remove_card", methods=["POST"])
def remove_card():
    require_login()
    check_csrf()

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]

    if not deck_id.isdigit() or not card_id.isdigit():
        abort(403)

    deck_id = int(deck_id)
    card_id = int(card_id)

    deck = decks.get_deck(deck_id)

    if not deck:
        abort(404)

    if deck["user_id"] != session["user_id"]:
        abort(403)

    cards = decks.get_cards(deck_id)

    if not any(card["id"] == card_id for card in cards):
        abort(404)

    decks.remove_card(card_id)

    return redirect("/edit_cards/" + str(deck_id))

@app.route("/add_comment", methods=["POST"])
def add_comment():
    require_login()
    check_csrf()

    deck_id = request.form["deck_id"]

    if not deck_id.isdigit():
        abort(403)

    deck_id = int(deck_id)
    deck = decks.get_deck(deck_id)

    if not deck:
        abort(404)

    content = request.form["content"].strip()

    errors = []

    if not content:
        errors.append("Comment cannot be empty!")

    if len(content) > 1000:
        errors.append("Comment cannot exceed 1000 characters!")

    if errors:
        for error in errors:
            flash(error)

        cards = decks.get_cards(deck_id)
        tags = decks.get_deck_tags(deck_id)
        all_comments = comments_db.get_comments(deck_id)
        return render_template("show_deck.html", deck=deck, cards=cards, tags=tags, comments=all_comments, comment_content=content)

    comments_db.add_comment(deck_id, session["user_id"], content)

    return redirect("/deck/" + str(deck_id))

@app.route("/remove_comment", methods=["POST"])
def remove_comment():
    require_login()
    check_csrf()

    comment_id = request.form["comment_id"]
    deck_id = request.form["deck_id"]

    if not comment_id.isdigit() or not deck_id.isdigit():
        abort(403)

    comment_id = int(comment_id)
    deck_id = int(deck_id)

    comment = comments_db.get_comment(comment_id)

    if not comment:
        abort(404)

    if comment["deck_id"] != deck_id:
        abort(404)

    if comment["user_id"] != session["user_id"]:
        abort(403)

    comments_db.remove_comment(comment_id)

    return redirect("/deck/" + str(deck_id))

@app.route("/register")
def register():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    check_csrf()
    username = request.form["username"].strip()
    password1 = request.form["password1"].strip()
    password2 = request.form["password2"].strip()

    errors = []

    if not username or len(username) < 3 or len(username) > 20:
        errors.append("Username must be between 3 and 20 characters!")

    if not password1 or len(password1) < 8:
        errors.append("Password must be at least 8 characters long!")

    if password1 != password2:
        errors.append("Passwords do not match!")

    if errors:
        for error in errors:
            flash(error)
        return render_template("register.html", username=username)

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("Username is already taken.")
        return render_template("register.html", username=username)

    flash("Account created successfully!")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    errors = []

    if not username:
        errors.append("Username cannot be empty.")

    if not password:
        errors.append("Password cannot be empty.")

    if errors:
        for error in errors:
            flash(error)
        return render_template("login.html", username=username)

    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")

    flash("Wrong username or password.")
    return render_template("login.html", username=username)

@app.route("/logout", methods=["POST"])
def logout():
    require_login()
    check_csrf()

    session.clear()
    return redirect("/")