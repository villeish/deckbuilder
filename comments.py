"""Operations for comments."""
import db


def get_comments(deck_id):
    """Return all comments belonging to a deck."""
    sql = """SELECT comments.id,
                    comments.content,
                    comments.sent_at,
                    comments.user_id,
                    users.username
             FROM comments, users
             WHERE comments.user_id = users.id AND
                   comments.deck_id = ?
             ORDER BY comments.id DESC"""
    return db.query(sql, [deck_id])

def get_comment(comment_id):
    """Return a comment by its ID."""
    sql = """SELECT id, user_id, deck_id
             FROM comments
             WHERE id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def add_comment(deck_id, user_id, content):
    """Add a comment to a deck."""
    sql = """INSERT INTO comments (content, sent_at, user_id, deck_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, deck_id])

def remove_comment(comment_id):
    """Delete a comment by its ID."""
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])
