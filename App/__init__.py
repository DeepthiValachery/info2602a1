from .app import db, app
from .models import Pokemon
import csv

with open('App/pokemon.csv', newline=' ', mode='r') as file:
    input = csv.reader(file)
    next(input, None)
    for abilities,against_bug,against_dark,against_dragon,against_electric,against_fairy,against_fight,against_fire,against_flying,against_ghost,against_grass,against_ground,against_ice,against_normal,against_poison,against_psychic,against_rock,against_steel,against_water,attack,base_egg_steps,base_happiness,base_total,capture_rate,classfication,defense,experience_growth,height_m,hp,japanese_name,name,percentage_male,pokedex_number,sp_attack,sp_defense,speed,type1,type2,weight_kg,generation,is_legendary in input:
        pokemon = Pokemon(pokeid=pokedex_number, name=name, attack=attack, defense=defense, hp=hp, height=height_m, sp_attack=sp_attack, sp_defense=sp_defense, speed=speed, type1=type1, type2=type2, weight=weight_kg)
        if not type2:
            pokemon.type2 = None
        if not height_m:
            pokemon.height = None
        if not weight_kg:
            pokemon.weight = None
        db.session.add(pokemon)
        db.session.commit()