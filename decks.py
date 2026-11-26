"""Operations for decks, cards and tags."""
import db


def add_deck(name, description, user_id):
    """Create a deck and return its ID."""
    sql = """INSERT INTO decks (name, description, user_id)
             VALUES (?, ?, ?)"""
    db.execute(sql, [name, description, user_id])

    deck_id = db.last_insert_id()

    return deck_id

def get_decks(page, page_size):
    """Return a page of decks with their creators."""
    sql = """SELECT decks.id,
                    decks.name,
                    decks.description,
                    users.id user_id,
                    users.username
             FROM decks JOIN users ON decks.user_id = users.id
             ORDER BY decks.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_deck(deck_id):
    """Return a deck and its creator by deck ID."""
    sql = """SELECT decks.id,
                    decks.name,
                    decks.description,
                    users.id user_id,
                    users.username
             FROM decks, users
             WHERE decks.user_id = users.id AND
                   decks.id = ?"""
    result = db.query(sql, [deck_id])
    return result[0] if result else None

def deck_count():
    """Return the total number of decks."""
    sql = "SELECT COUNT(*) FROM decks"
    return db.query(sql)[0][0]

def get_cards(deck_id):
    """Return all cards belonging to a deck."""
    sql = """SELECT id, card_name, quantity
             FROM deck_cards
             WHERE deck_id = ?"""
    return db.query(sql, [deck_id])

def remove_deck(deck_id):
    """Delete a deck and its cards."""
    sql = "DELETE FROM deck_cards WHERE deck_id = ?"
    db.execute(sql, [deck_id])

    sql = "DELETE FROM decks WHERE id = ?"
    db.execute(sql, [deck_id])

def add_card(deck_id, card_name, quantity):
    """Add a card to a deck."""
    sql = """SELECT id, quantity FROM deck_cards
             WHERE deck_id = ? AND LOWER(card_name) = LOWER(?)"""
    result = db.query(sql, [deck_id, card_name])

    if result:
        card_id = result[0]["id"]
        new_quantity = result[0]["quantity"] + quantity

        if new_quantity > 99:
            return False

        update_card_quantity(card_id, new_quantity)
        return True
    sql = """INSERT INTO deck_cards (deck_id, card_name, quantity)
             VALUES (?, ?, ?)"""
    db.execute(sql, [deck_id, card_name, quantity])
    return True

def update_deck(deck_id, name, description):
    """Update a deck's name and description."""
    sql = """UPDATE decks SET name = ?,
                              description = ?
                          WHERE id = ?"""
    db.execute(sql, [name, description, deck_id])

def update_card(card_id, card_name, quantity):
    """Update a card's name and quantity."""
    sql = """UPDATE deck_cards
             SET card_name = ?, quantity = ?
             WHERE id = ?"""
    db.execute(sql, [card_name, quantity, card_id])

def update_card_quantity(card_id, quantity):
    """Update a card's quantity."""
    sql = """UPDATE deck_cards SET quantity = ?
             WHERE id = ?"""
    db.execute(sql, [quantity, card_id])

def remove_card(card_id):
    """Delete a card from a deck."""
    sql = "DELETE FROM deck_cards WHERE id = ?"
    db.execute(sql, [card_id])

def find_decks(query, tag_ids, page, page_size):
    """Search decks by name, description and tags."""
    sql = """SELECT decks.id,
                    decks.name,
                    decks.description,
                    users.id user_id,
                    users.username
             FROM decks JOIN users ON decks.user_id = users.id"""

    conditions = []
    params = []

    if query:
        conditions.append("(decks.name LIKE ? OR decks.description LIKE ?)")
        like = "%" + query + "%"
        params.extend([like, like])

    if tag_ids:
        placeholders = ",".join("?" for tag_id in tag_ids)
        conditions.append("""EXISTS (
                                 SELECT 1 FROM deck_tags
                                 WHERE deck_tags.deck_id = decks.id
                                 AND deck_tags.tag_id IN (""" + placeholders + """)
                             )""")
        params.extend(tag_ids)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY decks.id DESC LIMIT ? OFFSET ?"

    limit = page_size
    offset = page_size * (page - 1)
    params.extend([limit, offset])

    return db.query(sql, params)

def find_deck_count(query, tag_ids):
    """Return the number of decks matching the search filters."""
    sql = "SELECT COUNT(*) FROM decks"

    conditions = []
    params = []

    if query:
        conditions.append("(name LIKE ? OR description LIKE ?)")
        like = "%" + query + "%"
        params.extend([like, like])

    if tag_ids:
        placeholders = ",".join("?" for tag_id in tag_ids)
        conditions.append("""EXISTS (
                                 SELECT 1 FROM deck_tags
                                 WHERE deck_tags.deck_id = decks.id
                                 AND deck_tags.tag_id IN (""" + placeholders + """)
                             )""")
        params.extend(tag_ids)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    result = db.query(sql, params)
    return result[0][0]

def add_deck_tag(deck_id, tag_id):
    """Add a tag to a deck."""
    sql = """INSERT INTO deck_tags (deck_id, tag_id)
             VALUES (?, ?)"""
    db.execute(sql, [deck_id, tag_id])

def remove_deck_tags(deck_id):
    """Remove all tags associated with a deck."""
    sql = """DELETE FROM deck_tags
             WHERE deck_id = ?"""
    db.execute(sql, [deck_id])

def get_tags():
    """Return all available tags."""
    sql = """SELECT id, name
             FROM tags
             ORDER BY name"""
    return db.query(sql)

def get_deck_tags(deck_id):
    """Return all tags in a deck."""
    sql = """SELECT tags.id, tags.name
             FROM tags JOIN deck_tags
                  ON tags.id = deck_tags.tag_id
             WHERE deck_tags.deck_id = ?
             ORDER BY tags.name"""
    return db.query(sql, [deck_id])
