#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'
@app.route('/restaurant', methods=['GET'])
def getRestaurants():
    restaurants=Restaurant.query.all()
    restaurants_to_dict=[restaurant.to_dict(include_pizzas=True) for  restaurant in restaurants ]
    response = make_response(restaurants_to_dict,200)

    return response

@app.route('/restaurant/<int:id>', methods=['GET'])
def getById(id):
    restaurant=Restaurant.query.filter_by(id = id).first()
    if restaurant :
        return make_response(restaurant.to_dict(include_pizzas=True),200)
    else:
        return jsonify({'error':'Restaurant not found'}) ,404

@app.route('/restaurant/<int:id>' ,methods=['DELETE'])
def delete(id):
    restaurant=Restaurant.query.filter_by(id =Restaurant.id).first()
    if restaurant :
        db.session.delete(restaurant)
        db.session.commit()
        return jsonify(restaurant.to_dict(),405)
    else:
        return jsonify({'error':'Restaurant not found'}) ,404
    
@app.route('/pizzas', methods=['GET'])
def getPizzas():
    pizzas=Pizza.query.all()
    pizzas_to_dict=[pizza.to_dict() for  pizza in pizzas ]
    response = make_response(pizzas_to_dict,200)

    return response 

@app.route('/restaurant_pizzas' , methods=['POST'])
def restaurant_pizzas():
    price = request.json.get("price")
    pizza_id= request.json.get("pizza_id")
    restaurant_id=request.json.get("restaurant_id")

    if not all([price, pizza_id, restaurant_id]):
        return jsonify({"errors": ["validation errors"]}), 400

    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = db.session.query(Pizza).get(pizza_id)
    restaurant = db.session.query(Restaurant).get(restaurant_id)

    if not (pizza and restaurant):
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

    try:
        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        return jsonify(new_restaurant_pizza.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True) 
