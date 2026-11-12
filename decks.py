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

def find_decks(query):
    sql = """SELECT id, name
             FROM decks
             WHERE name LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])