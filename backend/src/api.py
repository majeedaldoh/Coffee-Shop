import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()
# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drinks_detail = [drink.short() for drink in drinks]
    if drinks == 0: 
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks_detail
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-details', methods=['GET'])
@require_auth('get:drinks-detail')
def get_drinks_details(jwt):

    try:
        drinks = Drink.query.all()
        drinks_detail = [drink.long() for drink in drinks]
        if len(drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks_detail
        },200)

    except: 
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@require_auth('post:drinks')
def post_drink():

    try:
        body = request.get_json()
        new_drink_title = body['title']
        new_drink_recipe = body['recipe']

        new_drink = Drink(title = new_drink_title, recipe = json.dumps(new_drink_recipe))
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        },200)

    except: 
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('drinks/<int:drink_id>', methods=['PATCH'])
@require_auth('patch:drinks')
def update_drink(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none
    if drink is None:
        abort(404)
    try:
        body = request.get_json()
        
        if 'title' in body:
            drink.title = body['title']
            
        if 'recipe' in body:
            drink.recipe = body['recipe']
            
            drink.update()

            return jsonify({
            'success': True,
            'drinks': [drink.long()]
        },200)

    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['DELETE'])
@require_auth('delete:drinks')
def delete_drink(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none

    if drink is None:
        abort(404)
    try:
        drink.delete()
        
        return jsonify({
            'success': True,
            'deleted': drink_id
            },200)
    except: 
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': "unprocessable"
    },422)

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "not found"
    },404)

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response