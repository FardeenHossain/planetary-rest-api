from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    basedir, 'planets.db')

db = SQLAlchemy(app)


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
    earth = Planet(name='Earth', mass=5.972e24, radius=6371,
                   distance=149.6e6)

    mars = Planet(name='Mars', mass=6.39e23, radius=3389.5,
                  distance=227.9e6)

    saturn = Planet(name='Saturn', mass=5.683e26, radius=58232,
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
    return jsonify(data=planets_list)


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
    name = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


if __name__ == '__main__':
    app.run()
