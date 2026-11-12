CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);
CREATE TABLE decks (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE deck_cards (
    id INTEGER PRIMARY KEY,
    deck_id INTEGER REFERENCES decks,
    card_name TEXT,
    quantity INTEGER
);