from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class UserPokemon(db.Model):
  id = db.Column('id', db.Integer, primary_key=True)
  userId = db.Column('user_ID', db.Integer, db.ForeignKey(user.id))
  pokeId = db.Column('pokemon_ID', db.Integer, db.ForeignKey(Pokemon.pokeId))
  name = db.Column(db.String(50))
  pokemen = db.relationship('Pokemon')
  pass

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)

  pass

class Pokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  pass
