import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink,desc
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type, Authorization'
    )
    response.headers.add(
        'Access-Control-Allow-Methods', 'GET,POST,PATH,PATCH,DELETE'
    )

    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()


@app.route('/drinks', methods=['GET'])
def getDrinks():
    try:
        drinks = Drink.query.all()
        formattedDrinks = [drink.short() for drink in drinks]
        
        print(formattedDrinks)

        return jsonify({
            "success": True,
            "drinks": formattedDrinks
        })

    except:
        print(sys.exc_info())
        abort(404)
    

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinkDetail(jwt):
    try:
        drinks = Drink.query.all()
        formattedDrinks = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": formattedDrinks
        })
    except:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createDrink(jwt):
    try:
        body = request.get_json()
        
        jsonRecipe = json.dumps(body["recipe"])

        drink = Drink(
            title = body["title"],
            recipe = jsonRecipe
        )

        
        drink.insert()
    
        drinks = Drink.query.all()
        formattedDrinks = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': formattedDrinks
        })
    except:
        print(sys.exc_info())
        abort(422)


@app.route('/drinks/<int:drinkId>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updateDrink(jwt,drinkId):
    try:
        body = request.get_json()
        drink = Drink.query.get(drinkId)
        
        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body: 
            drink.recipe = json.dumps(body['recipe'])

        drink.update()
        
        updatedDrink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': updatedDrink
        })
    except:
        print(sys.exc_info())
        abort(422)


@app.route('/drinks/<int:drinkId>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrink(jwt,drinkId):
    try:
        drink = Drink.query.get(drinkId)
        id = drink.id

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })
    except:
        abort(422)


'''
ERROR HANDLING
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def notFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resourve not found"
    }), 404


class AuthError(Exception):
    def __init__(self, error, statusCode):
        self.error = error
        self.statusCode = statusCode



if __name__ == "__main__":
    app.run(debug=True)