from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from sqlalchemy import Column, Integer, String, Float
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'secret-key'  # Change this IRL

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed')
def db_seed():
    earth = Planet(planet_name='Earth', mass=5.972e24, radius=6371,
                   distance=149.6e6)

    mars = Planet(planet_name='Mars', mass=6.39e23, radius=3389.5,
                  distance=227.9e6)

    saturn = Planet(planet_name='Saturn', mass=5.683e26, radius=58232,
                    distance=1.434e9)

    test_user = User(first_name='Fardeen', last_name='Hossain',
                     email='fardeen@email.com', password='password')

    db.session.add(earth)
    db.session.add(mars)
    db.session.add(saturn)
    db.session.add(test_user)

    db.session.commit()
    print('Database seeded!')


@app.route('/')
def home():
    return jsonify(message='Hello from the Planetary API!'), 200


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(
            message="Sorry " + name + ", you are not old enough"), 401
    else:
        return jsonify(message="Welcome " + name)


@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(
            message="Sorry " + name + ", you are not old enough"), 401
    else:
        return jsonify(message="Welcome " + name)


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)


@app.route('/planets/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="That planet does not exists"), 404


@app.route('/add_planet', methods=['POST'])
@jwt_required()
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message="That planet already exists"), 409
    else:
        mass = float(request.form['mass'])
        radius = float(request.form['radius'])
        distance = float(request.form['distance'])

        new_planet = Planet(planet_name=planet_name, mass=mass, radius=radius,
                            distance=distance)

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="Plannet added"), 201


@app.route('/update_planet/<int:planet_id>', methods=['PUT'])
@jwt_required()
def update_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message="Planet updated"), 202
    else:
        jsonify(message="That planet does not exist"), 404


@app.route('/remove_planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def remove_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="Planet removed"), 202
    else:
        return jsonify(message="That planet does not exist"), 404


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email,
                    password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token)
    else:
        return jsonify(message="Invalid email or password"), 401


# Database models
class User(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'name', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run()
