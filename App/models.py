from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UserPokemon(db.Model):
  uid = db.Column('uid', db.Integer, primary_key=True)
  id = db.Column('id', db.Integer, db.ForeignKey('user.id'))
  pokeid = db.Column('pokeid', db.Integer, db.ForeignKey('Pokemon.pokeid'))
  name = db.Column(db.String(50))
  pokemen = db.relationship('Pokemon')

  def toDict(self):
    return{
      'name':self.name,
      'stats':self.pokemon.toDict()
    }
  pass

class User(db.Model):
  id = db.Column('id', db.Integer, primary_key=True)
  username = db.Column('username', db.String(80), unique=True, nullable=False)
  email = db.Column('email', db.String(120), unique=True, nullable=False)
  password = db.Column('password', db.String(120), unique=True, nullable=False)

  def toDict(self):
    return {
      "id": self.id,
      "username": self.username,
      "email": self.email,
      "password": self.password
    }

  #must have passwordSet, passwordCheck
  pass

class Pokemon(db.Model):
  pokeid = db.Column('pokeid', db.Integer, primary_key=True)
  name = db.Column('name', db.String(50), nullable=False)
  attack = db.Column('attack', db.Integer, nullable=False)
  defense = db.Column('defense', db.Integer, nullable=False)
  hp = db.Column('hp', db.Integer, nullable=False)
  height = db.Column('height', db.Integer, nullable=True)
  sp_attack = db.Column('sp_attack', db.Integer, nullable=False)
  sp_defense = db.Column('sp_defense', db.Integer, nullable=False)
  speed = db.Column('speed', db.Integer, nullable=False)
  weight = db.Column('weight', db.Integer, nullable=True)
  type1 = db.Column('type1', db.String(50), nullable=False)
  type2 = db.Column('type2', db.String(50), nullable=True)
  
  def toDict(self):
    return {
      "pokeid": self.pokeid,
      "name": self.name,
      "attack": self.attack,
      "defense": self.defense,
      "hp": self.hp,
      "height": self.height,
      "sp_attack": self.sp_attack,
      "sp_defense": self.sp_defense,
      "speed": self.speed,
      "weight": self.weight,
      "type1": self.type1,
      "type2": self.type2
    }
  pass