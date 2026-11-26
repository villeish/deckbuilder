"""Database operations for user accounts."""
from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    """Return a user by their ID."""
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_user_stats(user_id):
    """Return the number of decks and comments created by a user."""
    sql = """SELECT
                 (SELECT COUNT(*) FROM decks
                  WHERE user_id = ?) AS deck_count,
                 (SELECT COUNT(*) FROM comments
                  WHERE user_id = ?) AS comment_count"""
    result = db.query(sql, [user_id, user_id])
    return result[0]

def get_decks(user_id):
    """Return all decks created by a user."""
    sql = "SELECT id, name FROM decks WHERE user_id = ? ORDER BY id DESC"
    return db.query(sql, [user_id])

def create_user(username, password):
    """Create a new account."""
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    """Check the login credentials and return the user ID if valid."""
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        return user_id

    return None
