"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users,Planets,Favorites,Characters
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#### Endpoints ####


# [GET] /characters - Obtener todos los personajes
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Characters.query.all()
    characters_list = [
        {
            'character_id': character.character_id,
            'name': character.name,
            'species': character.species,
            'homeworld': character.homeworld,
            'gender': character.gender
        }
        for character in characters
    ]
    return jsonify(characters_list), 200


# [GET] /character/<int:character_id> - Obtener la información de un personaje por ID
@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Characters.query.filter_by(character_id=character_id).first()
    if character is None:
        return jsonify({"message": "Character not found"}), 404

    character_data = {
        'character_id': character.character_id,
        'name': character.name,
        'species': character.species,
        'homeworld': character.homeworld,
        'gender': character.gender
    }
    return jsonify(character_data), 200


# [POST] /character - Agregar un personaje
@app.route('/character', methods=['POST'])
def add_character():
    data = request.get_json()
    if 'name' not in data or 'species' not in data or 'homeworld' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_character = Characters(
        name=data['name'],
        species=data['species'],
        homeworld=data['homeworld'],
        gender=data.get('gender', None)
    )
    db.session.add(new_character)
    db.session.commit()

    return jsonify({
        "message": "Character added successfully",
        "character_id": new_character.character_id,
        "name": new_character.name
    }), 201


# [PUT] /character/<int:character_id> - Modificar personaje
@app.route('/character/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    data = request.get_json()
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    character.name = data.get('name', character.name)
    character.species = data.get('species', character.species)
    character.homeworld = data.get('homeworld', character.homeworld)
    character.gender = data.get('gender', character.gender)
    db.session.commit()

    return jsonify({
        "message": "Character updated successfully",
        "character_id": character.character_id,
        "name": character.name
    }), 200


# [DELETE] /character/<int:character_id> - Eliminar personaje
@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    db.session.delete(character)
    db.session.commit()

    return jsonify({
        "message": "Character deleted successfully",
        "character_id": character_id
    }), 200

#### Planets ####

# [GET] /planets - Obtener todos los planetas
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_list = [
        {
            'planet_id': planet.planet_id,
            'name': planet.name,
            'climate': planet.climate,
            'terrain': planet.terrain,
            'population': planet.population
        }
        for planet in planets
    ]
    return jsonify(planets_list), 200


# [GET] /planet/<int:planet_id> - Obtener la información de un planeta por ID
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.filter_by(planet_id=planet_id).first()
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404

    planet_data = {
        'planet_id': planet.planet_id,
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain,
        'population': planet.population
    }
    return jsonify(planet_data), 200


# [POST] /planet - Agregar un planeta
@app.route('/planet', methods=['POST'])
def add_planet():
    data = request.get_json()
    if 'name' not in data or 'climate' not in data or 'terrain' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_planet = Planets(
        name=data['name'],
        climate=data['climate'],
        terrain=data['terrain'],
        population=data.get('population', None)
    )
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({
        "message": "Planet added successfully",
        "planet_id": new_planet.planet_id,
        "name": new_planet.name
    }), 201


# [PUT] /planet/<int:planet_id> - Modificar planeta de la BD
@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.get_json()
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    planet.name = data.get('name', planet.name)
    planet.climate = data.get('climate', planet.climate)
    planet.terrain = data.get('terrain', planet.terrain)
    planet.population = data.get('population', planet.population)
    db.session.commit()

    return jsonify({
        "message": "Planet updated successfully",
        "planet_id": planet.planet_id,
        "name": planet.name
    }), 200


# [DELETE] /planet/<int:planet_id> - Eliminar planeta de la bd
@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({
        "message": "Planet deleted successfully",
        "planet_id": planet_id
    }), 200

#### Fin Planets ####


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
