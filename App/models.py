from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserPokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey("pokemon.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, user_id, pokemon_id, name):
        self.user_id = user_id
        self.pokemon_id = pokemon_id
        self.name = name

    def get_json(self):
        pokemon = Pokemon.query.get(self.pokemon_id)
        species = pokemon.name if pokemon else None
        return {
                "id": self.id, 
                "name": self.name, 
                "species": species
            }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    user_pokemon = db.relationship("UserPokemon", backref="user", lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def catch_pokemon(self, pokemon_id, name):
        user_pokemon = UserPokemon.query.filter_by(user_id=self.id, pokemon_id=pokemon_id, name=name)
        db.session.add(user_pokemon)
        db.session.commit()
        return user_pokemon

    def release_pokemon(self, pokemon_id, name):
        user_pokemon = UserPokemon.query.filter_by(id=pokemon_id, user_id=self.id, name=name).first()
        if user_pokemon:
            db.session.delete(user_pokemon)
            db.session.commit()
            return True
        return False

    def rename_pokemon(self, pokemon_id, name):
        user_pokemon = UserPokemon.query.filter_by(id=pokemon_id, user_id=self.id).first()
        if user_pokemon:
            user_pokemon.name = name
            db.session.commit()
            return user_pokemon
        return None

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    type2 = db.Column(db.String(50), nullable=True)  # Nullable secondary type
    user_pokemon = db.relationship("UserPokemon", backref="pokemon", lazy=True)

    def __init__(
        self,
        name,
        attack,
        defense,
        hp,
        height,
        weight,
        sp_attack,
        sp_defense,
        speed,
        type1,
        type2,
    ) -> None:
        self.name = name
        self.attack = attack
        self.defense = defense
        self.hp = hp
        self.height = height
        self.weight = weight
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed
        self.type1 = type1
        self.type2 = type2

    def get_json(self):
        return {
            "id": self.id,
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
            "type2": self.type2,
        }
