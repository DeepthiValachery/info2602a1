import os, csv
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
)

from .models import db, User, UserPokemon, Pokemon

# Configure Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config['JWT_HEADER_TYPE'] = ""
app.config['JWT_HEADER_NAME'] = "Cookie"


# Initialize App 
db = SQLAlchemy(app)
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)

# Initializer Function to be used in both init command and /init route
def initialize_db():
  db.drop_all()
  db.create_all()

@app.cli.command('init-db')
@with_appcontext
def init_db_command():
    initialize_db()
    print('Database initialized!')

def authenticate(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.passwordCheck(password):
    token = create_access_token(identity=username)
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response
  return jsonify(message="Invalid username or password"), 401

# ********** Routes **************
@app.route('/', methods=['GET'])
@jwt_required()
def index():
  return '<h1>Poke API v1.0</h1>'

@app.route('/init', methods=['GET'])
def init_app():
  initialize_db()
  ###print('Database initialized!')
  return jsonify({"message":"Database initialized!"}), 200

@app.route('/pokemon', methods=['GET'])
def listPokemon():
  allPokemon = Pokemon.query.all()
  pokemonData = [{"pokemon_id": pokemon.pokeid,
                  "attack": pokemon.attack,
                  "defense": pokemon.defense,
                  "sp_attack": pokemon.sp_attack,
                  "sp_defense": pokemon.sp_defense,
                  "speed": pokemon.speed,
                  "hp": pokemon.hp,
                  "height": pokemon.height,
                  "weight": pokemon.weight,
                  "type1": pokemon.type1,
                  "type2": pokemon.type2} for pokemon in allPokemon]
  return jsonify(pokemonData), 200

@app.route('/signup', methods=['POST'])
def signup():
  userdata = request.get_json()
  username = userdata.get('username')
  email = userdata.get('email')
  password = userdata.get('password')

  existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
  if existing_user:
    return jsonify({"message": "Username or email already exists"}), 409 #Conflict status code

  newuser = User(username=username, email=email)
  newuser.passwordSet(password)

  try:
    db.session.add(newuser)
    db.session.commit()
    return jsonify({"message": f"{username} created"}), 201 # created status code
  except IntegrityError:
    db.session.rollback()
    return jsonify({"message": "Username or email already exists"}), 409  # 409 Conflict status code

@app.route('/login', methods=['POST'])
def login():
  data = request.json
  username = data.get('username')
  password = data.get('password')

  user - User.query.filter_by(username=username).first()
  if not user or not check_password_hash(user.password, password):
    return jsonify(message='Bad username or password given'), 403   # Forbidden status code
  
  access_token = create_access_token(identity=username)
  return jsonify(access_token=access_token), 200 #OK status code

@app.route('/mypokemon', methods=['POST'])
@jwt_required()
def myPokemon():
  data = request.get_json()
  pokeid = data.get('pokeid')
  name = data.get('name')

  pokemon = Pokemon.query.get(pokeid)
  if not pokemon:
    return jsonify(error = f"{pokeid} is not a valid pokemon id"), 400 #bad request status code

  
  new_pokemon = UserPokemon(user_id=current_user.id, pokeid=pokeid, name=name)
  db.session.add(new_pokemon)
  db.session.commit()
  return jsonify(message=f'{name} captured with id: {pokeid}', user_pokemon_id=new_pokemon.id), 200 #OK status code

@app.route('/mypokemon', methods=['GET'])
@jwt_required()
def myListPoke():
  pokemonData = []
  allmypokemon = UserPokemon.query.filter_by(user_id=current_user.id).all()
  for myPokemon in allmypokemon:
    pokemonData.append({
      "id": UserPokemon.id,
      "name": UserPokemon.name,
      "species": UserPokemon.species
    })
  return jsonify(pokemonData), 200

@app.route('/mypokemon/<int:n>', methods=['GET'])
@jwt_required()
def getPokemon(n):
  pokemon = UserPokemon.query.filter_by(id=n, user_id=current_user.id).first()
  if not pokemon:
    return jsonify(message = f"Id {n} is invalid or does not belong to {current_user.username}"), 404 #Not found
  return jsonify(pokemon.toDict()), 200

@app.route('/mypokemon/<int:n>', methods=['PUT'])
@jwt_required()
def update(n):
  data = request.get_json()
  new_name = data.get('name')

  if not new_name or new_name.strip() == '':
    return jsonify(message='Invalid Pokemon name'), 400

  pokemon = UserPokemon.query.filter_by(id=n, user_id=current_user.id).first()
  if not pokemon:
    return jsonify(message=f"No Pokemon captured with id {n}"), 404

  try:
    pokemon.name = new_name
    db.session.commit()
    return jsonify(message=f"{pokemon.name} renamed to {new_name}"), 200
  except:
    db.session.rollback()
    return jsonify(message='Pokemon could not be named'), 500

@app.route('/mypokemon/<int:n>', methods=['DELETE'])
@jwt_required()
def delete(n):
  pokemon = UserPokemon.query.filter_by(id=n, user_id=current_user.id).first()
  if not pokemon:
    return jsonify(error=f"Id {n} is invalid or does not belong to {current_user.username}"), 404

  try:
    db.session.delete(pokemon)
    db.session.commit()
    return jsonify(message=f"{pokemon.name} released"), 200
  except:
    db.session.rollback()
    return jsonify(error='Error releasing Pokemon'), 500

  if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)

