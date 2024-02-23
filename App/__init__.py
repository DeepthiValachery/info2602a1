from .app import *
from .models import *
import csv

def initialize_db():
    with open('pokemon.csv') as file:
        input = csv.reader(file)
        next(input, None)
        for row in input:
            abilities,against_bug,against_dark,against_dragon,against_electric,against_fairy,against_fight,against_fire,against_flying,against_ghost,against_grass,against_ground,against_ice,against_normal,against_poison,against_psychic,against_rock,against_steel,against_water,attack,base_egg_steps,base_happiness,base_total,capture_rate,classfication,defense,experience_growth,height_m,hp,japanese_name,name,percentage_male,pokedex_number,sp_attack,sp_defense,speed,type1,type2,weight_kg,generation,is_legendary = row
            
            pokemon = Pokemon(pokeid=int(pokedex_number), name=name, attack=int(attack), defense=int(defense), hp=int(hp), height=int(height_m), sp_attack=int(sp_attack), sp_defense=int(sp_defense), speed=int(speed), type1=type1, 
            type2=type2 if type2 else None, weight=int(weight_kg))
            
            db.session.commit()
if __name__ == "__main__":
    initialize_db()