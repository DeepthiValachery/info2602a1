import os, csv
from flask import Flask, jsonify, request
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from .models import db, User, UserPokemon, Pokemon

# Configure Flask App
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "MySecretKey"
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_HEADER_TYPE"] = ""
app.config["JWT_HEADER_NAME"] = "Cookie"


# Initialize App
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)


# Initializer Function to be used in both init command and /init route
def initialize_db():
    db.drop_all()
    db.create_all()

    # Read data from pokemon.csv and create Pokemon objects
    with open("pokemon.csv", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:

            # Check if the height, weight, type2 key exists in the row
            height = int(row["height"]) if "height" in row and row["height"] else None

            weight = int(row["weight"]) if "weight" in row and row["weight"] else None

            type2 = row["type2"] if "type2" in row and row["type2"] else None

            # Create a Pokemon object
            pokemon = Pokemon(
                name=row["name"],
                attack=int(row["attack"]),
                defense=int(row["defense"]),
                hp=int(row["hp"]),
                height=height,
                sp_attack=int(row["sp_attack"]),
                sp_defense=int(row["sp_defense"]),
                speed=int(row["speed"]),
                weight=weight,
                type1=row["type1"],
                type2=type2,
            )

            # Add the Pokemon object to the session
            db.session.add(pokemon)
    db.session.commit()


def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity=username)
        response = jsonify(access_token=token)
        set_access_cookies(response, token)
        return response
    return jsonify(error="bad username/password given"), 401


# **** Routes ******
# GET Root
@app.route("/", methods=["GET"])
def index():
    return "<h1>Poke API v1.0</h1>"


# GET Initialize App
@app.route("/init", methods=["GET"])
def init_app():
    initialize_db()
    return jsonify({"message": "Database Initialized!"}), 200


# GET List Pokemon
@app.route("/pokemon", methods=["GET"])
def listPokemon():
    allPokemon = Pokemon.query.all()
    pokemonData = [
        {
            "pokemon_id": pokemon.id,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "sp_attack": pokemon.sp_attack,
            "sp_defense": pokemon.sp_defense,
            "speed": pokemon.speed,
            "hp": pokemon.hp,
            "height": pokemon.height,
            "weight": pokemon.weight,
            "type1": pokemon.type1,
            "type2": pokemon.type2,
        }
        for pokemon in allPokemon
    ]
    return jsonify(pokemonData), 200


# POST Sign Up
@app.route("/signup", methods=["POST"])
def signup():
    userdata = request.json
    if userdata is None:
        return jsonify(message="No JSON data provided"), 400

    username = userdata.get("username")
    email = userdata.get("email")
    password = userdata.get("password")

    if not username or not email or not password:
        return (
            jsonify(
                error="Invalid request. Username, email, and password are required."
            ),
            400,
        )

    existing_user = User.query.filter_by(username=username).first()
    exist_email = User.query.filter_by(email=email).first()

    if existing_user or exist_email:
        return jsonify(error="username or email already exists"), 400

    try:
        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()
        return (
            jsonify({"message": f"{new_user.username} created"}),
            201,
        )  # 201 Created status code

    except IntegrityError:
        db.session.rollback()
        return (
            jsonify({"message": "Username or email already exists"}),
            400,
        )  # 400 Bad Request status code


# POST Log In
@app.route("/login", methods=["POST"])
def user_login_view():
    data = request.json
    response = login_user(data["username"], data["password"])
    if not response:
        return jsonify(message="bad username or password given"), 403
    return response


# POST Save my Pokemon
@app.route("/mypokemon", methods=["POST"])
@jwt_required()
def myPokemon():
    user_id = get_jwt_identity()
    data = request.json

    if data is None:
        return jsonify(message="No JSON data provided"), 400

    pokemon_id = data.get("pokemon_id")
    name = data.get("name")

    if pokemon_id is None:
        return jsonify(error="Pokemon ID is missing"), 400

    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        return jsonify(error=f"{pokemon_id} is not a valid pokemon id"), 400

    new_pokemon = UserPokemon(user_id, pokemon_id, name)
    db.session.add(new_pokemon)
    db.session.commit()
    return (
        jsonify(
            message=f"{name} captured with id: {pokemon_id}",
            user_pokemon_id=new_pokemon.id,
        ),
        201,
    )


# GET List Pokemeon
@app.route("/mypokemon", methods=["GET"])
@jwt_required()
def myListPokemon():
    user_id = get_jwt_identity()

    # get the user object of the authenticated user
    user = UserPokemon.query.filter_by(user_id=user_id).all()
    # converts objects to list of dictionaries
    poke_json = [UserPokemon.get_json() for UserPokemon in user]
    return jsonify(poke_json), 201


# GET my Pokemon
@app.route("/mypokemon/<int:n>", methods=["GET"])
@jwt_required()
def getPokemon(n):
    poke = UserPokemon.query.get(n)
    # poke = UserPokemon.query.filter_by(id=n).first()
    user_id = get_jwt_identity()

    if not poke or poke.user.name != user_id:
        return jsonify(error=f"Id {n} is invalid or does not belong to {user_id}"), 401

    return jsonify(poke.get_json()), 200


# PUT Update Pokemon
@app.route("/mypokemon/<int:n>", methods=["PUT"])
@jwt_required()
def update(pokemon_id):
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.filter_by(username=user_id).first()

    if not user:
        return jsonify(error=f"User {user_id} not found"), 404

    userpoke = UserPokemon.query.filter_by(pokemon_id=pokemon_id).first()

    if not userpoke:
        return (
            jsonify(
                error=f"Id {pokemon_id} is invalid or does not belong to {user_id}"
            ),
            401,
        )

    old_name = userpoke.name
    new_name = data.get("name")

    if not new_name:
        return jsonify(error="New name is missing"), 400

    user.rename_pokemon(userpoke.pokemon_id, new_name)
    return jsonify(message=f"{old_name} renamed to {new_name}"), 200


# DELETE Delete Pokemon
@app.route("/mypokemon/<int:n>", methods=["DELETE"])
@jwt_required()
def delete(pokemon_id):
    user_id = get_jwt_identity()
    user = User.query.filter_by(username=user_id).first()

    if not user:
        return jsonify(error=f"User {user_id} not found"), 404

    poke = UserPokemon.query.filter_by(pokemon_id=pokemon_id).first()

    if not poke:
        return jsonify(error=f"Id {pokemon_id} is invalid or does not belong to {user_id}"), 401

    pokemon_name = poke.name

    user.release_pokemon(poke.id, pokemon_name)
    return jsonify(message=f"{pokemon_name} released"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
