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
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
    card_name TEXT,
    quantity INTEGER
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE deck_tags (
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (deck_id, tag_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    deck_id INTEGER REFERENCES decks
);

CREATE INDEX idx_deck_comments ON comments (deck_id);
