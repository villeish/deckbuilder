# deckbuilder
- Sovelluksessa käyttäjä pystyy tallentamaan ja jakamaan magic the gathering-pakkojaan.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan pakkoja
- Käyttäjä pystyy lisäämään pakkoihin kortteja ja luokitteluja
- käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään
- käyttäjä näkee sovellukseen lisätyt pakat
- käyttäjäsivu näyttää käyttäjän lisäämät pakat
- käyttäjä pystyy etsimään pakkoja nimen tai luokittelun perusteella
- käyttäjä pystyy valitsemaan esimerkiksi seuraavia luokitteluja: aggro, control, midrange
- Pääasiallinen tietokohde on pakka ja toissijainen tietokohde on kommentit. 

# Asennus
Asenna flask-kirjasto:

$ pip install flask

Luo ja alusta tietokanta:

$ sqlite3 database.db < schema.sql

$ sqlite3 database.db < init.sql

tai

$ python3 init_db.py

# Testaus

Rekisteröi käyttäjä ja kirjaudu sisään. Kokeile luoda pakka, lisätä kortteja ja muokata niiden määrää tai etsiä ja poistaa pakkoja. Kokeile myös tehdä toinen käyttäjä ja katsoa toisen käyttäjän pakkoja.
