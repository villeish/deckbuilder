import db


def add_deck(name, description, user_id):
    sql = """INSERT INTO decks (name, description, user_id)
             VALUES (?, ?, ?)"""
    db.execute(sql, [name, description, user_id])

    deck_id = db.last_insert_id()

    return deck_id

def get_decks():
    sql = """SELECT decks.id,
                    decks.name,
                    decks.description,
                    users.id user_id,
                    users.username
             FROM decks JOIN users ON decks.user_id = users.id
             ORDER BY decks.id DESC"""
    return db.query(sql)

def get_deck(deck_id):
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

def get_cards(deck_id):
    sql = """SELECT id, card_name, quantity
             FROM deck_cards
             WHERE deck_id = ?"""
    return db.query(sql, [deck_id])

def remove_deck(deck_id):
    sql = "DELETE FROM deck_cards WHERE deck_id = ?"
    db.execute(sql, [deck_id])

    sql = "DELETE FROM decks WHERE id = ?"
    db.execute(sql, [deck_id])

def add_card(deck_id, card_name, quantity):
    sql = """SELECT id, quantity FROM deck_cards
             WHERE deck_id = ? AND card_name = ?"""
    result = db.query(sql, [deck_id, card_name])

    if result:
        card_id = result[0]["id"]
        new_quantity = result[0]["quantity"] + quantity
        update_card_quantity(card_id, new_quantity)
    else:
        sql = """INSERT INTO deck_cards (deck_id, card_name, quantity)
                 VALUES (?, ?, ?)"""
        db.execute(sql, [deck_id, card_name, quantity])

def update_deck(deck_id, name, description):
    sql = """UPDATE decks SET name = ?,
                              description = ?
                          WHERE id = ?"""
    db.execute(sql, [name, description, deck_id])

def update_card_quantity(card_id, quantity):
    sql = """UPDATE deck_cards SET quantity = ?
             WHERE id = ?"""
    db.execute(sql, [quantity, card_id])

def remove_card(card_id):
    sql = "DELETE FROM deck_cards WHERE id = ?"
    db.execute(sql, [card_id])

def find_decks(query, tag_ids):
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

    sql += " ORDER BY decks.id DESC"

    return db.query(sql, params)

def add_deck_tag(deck_id, tag_id):
    sql = """INSERT INTO deck_tags (deck_id, tag_id)
             VALUES (?, ?)"""
    db.execute(sql, [deck_id, tag_id])

def remove_deck_tags(deck_id):
    sql = """DELETE FROM deck_tags
             WHERE deck_id = ?"""
    db.execute(sql, [deck_id])

def get_tags():
    sql = """SELECT id, name
             FROM tags
             ORDER BY name"""
    return db.query(sql)

def get_deck_tags(deck_id):
    sql = """SELECT tags.id, tags.name
             FROM tags JOIN deck_tags
                  ON tags.id = deck_tags.tag_id
             WHERE deck_tags.deck_id = ?
             ORDER BY tags.name"""
    return db.query(sql, [deck_id])