from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UserPokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  pokeid = db.Column( db.Integer, db.ForeignKey('Pokemon.pokeid'), nullable=False)
  name = db.Column(db.String, nullable=False)

  pokemon = db.relationship('Pokemon', backref='captured_by', lazy=True)

  def toDict(self):
    return{
      'name':self.name,
      'pokemon':self.pokemon.toDict()
    }

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  email = db.Column(db.String(100), unique=True, nullable=False)
  password_hash = db.Column(db.String, unique=True, nullable=False)

  captured_pokemon = db.relationship('UserPokemon', backref='user', lazy=True)

  #must have passwordSet, passwordCheck
  def set_password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
  
  def toDict(self):
    return {
      "id": self.id,
      "username": self.username,
      "email": self.email
    }

class Pokemon(db.Model):
  pokeid = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  attack = db.Column(db.Integer, nullable=False)
  defense = db.Column(db.Integer, nullable=False)
  hp = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Integer, nullable=True)
  sp_attack = db.Column(db.Integer, nullable=False)
  sp_defense = db.Column(db.Integer, nullable=False)
  speed = db.Column(db.Integer, nullable=False)
  weight = db.Column(db.Integer, nullable=True)
  type1 = db.Column(db.String(50), nullable=False)
  type2 = db.Column(db.String(50), nullable=True)
  
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