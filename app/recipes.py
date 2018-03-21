import json
from json.decoder import JSONDecodeError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from flask import Blueprint, request, jsonify, make_response
from app import app, db, models

from flasgger import swag_from
from .serializers import RecipeSchema
from .helpers import token_required, check_password, check_mail, special_character, recipe_exists, category_exists
from .models import User, Category, Recipe


mod = Blueprint('recipes', __name__)

@mod.route('/recipe', methods=['POST'])
@token_required
@swag_from('docs/recipe_post.yml')
def add_recipe(current_user):
    """
    Post a new recipe.     
    """
    if not current_user:
          return jsonify({'message': 'Permission required'}), 401
    
    data = request.get_json()
    schema = RecipeSchema()
    try:
        recipe, errors = schema.loads(request.data)
    except JSONDecodeError:
        return jsonify({'message': 'Could not process the provided keys'}), 422
    if errors:
        return make_response(json.dumps({'errors': errors, 'status': False})), 422
    elif recipe_exists(data['title'].lower(), current_user.id):
        return jsonify({'message': 'Recipe with similar name already exists', 'status': False }), 422

    cat_exists = Category.query.filter(Category.id == data['category_id']).filter(Category.user_id == current_user.id).first()
    if cat_exists:
        my_recipe = Recipe(
            title=data['title'].lower(),
            ingredients=data['ingredients'],
            steps=data['steps'],
            category_id=data['category_id'],
            user_id=current_user.id)
        my_recipe.save()

        return jsonify({'message': 'Successfully added new Recipe', 'status': True, 'recipe': recipe}), 201
    return jsonify({'message':'Could not Find a matching category id.', 'status': False}), 403


@mod.route('/recipe', methods=['GET'])
@token_required
@swag_from('docs/recipe_get_all.yml')
def get_recipes(current_user):
    """
      Get all user's recipes.
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 6))
    except:
        return jsonify({'message': 'Ivalid page, per_page parameter'}), 422
    q = str(request.args.get('q','')).lower()

    output = []
    try:
        if q:
            recipes = Recipe.query.filter(Recipe.user_id == current_user.id).filter(Recipe.title.ilike('%'+q+'%')).paginate(page = page, per_page = per_page)
        else:
            recipes = Recipe.query.filter_by(user_id=current_user.id).paginate(page = page, per_page = per_page)
    except:
        return jsonify({'message': 'The requested URL was not found on the server'}), 404
           
    if not recipes:
        return jsonify({'message': 'No recipes available', 'status': False }), 

    for recipe in recipes.items: 
        recipee = {}
        recipee['id'] = recipe.id
        recipee['title'] = recipe.title
        recipee['ingredients'] = recipe.ingredients
        recipee['steps'] = recipe.steps
        recipee['category_id'] = recipe.category_id
        output.append(recipee)
            
    
    return jsonify({'recipes': output, 'pages': recipes.pages, 'page': recipes.page})
   


@mod.route('/recipe/<recipe_id>', methods=['GET'])
@token_required
@swag_from('docs/recipe_get_id.yml')
def get_recipe(current_user, recipe_id):
    """
    Get recipe by id.
    """
    recipe = Recipe.query.filter(Recipe.user_id == current_user.id).filter(Recipe.id == recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe is not available', 'status': False}), 404

    recipee = {}
    recipee['id'] = recipe.id
    recipee['title'] = recipe.title
    recipee['ingredients'] = recipe.ingredients
    recipee['steps'] = recipe.steps
    recipee['category_id'] = recipe.category_id

    return jsonify({'recipe': recipee})

@mod.route('/recipe/<recipe_id>', methods=['PUT'])
@token_required
@swag_from('docs/recipe_put.yml')
def update_recipe(current_user, recipe_id):
    """
    Edit recipe by id.   
    """
    if not current_user:
        return jsonify({'message': 'Permission required'}), 403
    data = request.get_json()
    schema = RecipeSchema()
    try:
        recipe, errors = schema.loads(request.data)
    except JSONDecodeError:
        return jsonify({'message': 'Could not process the provided keys'}), 422
    if errors:
        return make_response(json.dumps({'errors': errors, 'status': False})), 422

    my_recipe = Recipe.query.filter(Recipe.user_id == current_user.id).filter(Recipe.id == recipe_id).first()
    if not my_recipe:
        return jsonify({'message': 'Recipe is not available', 'status': False}), 404
    if recipe_exists(data['title'].lower(), current_user.id):
        return jsonify({'message': 'Recipe with similar name already exists', 'status': False }), 422
        
    cat_exists = Category.query.filter(Category.id == data['category_id']).filter(Category.user_id == current_user.id).first()
    if cat_exists:
        my_recipe.title = data['title'].lower()
        my_recipe.ingredients = data['ingredients']
        my_recipe.steps = data['steps']
        my_recipe.category_id = data['category_id']

        db.session.commit()
        return jsonify({'message': 'Successfully updated recipe', 'status': True, 'recipe': recipe}), 201
    return jsonify({'message':'Could not Find a matching category id.', 'status': False}), 404

@mod.route('/recipe/<recipe_id>', methods=['DELETE'])
@token_required
@swag_from('docs/recipe_delete.yml')
def delete_recipe(current_user, recipe_id):
    """
    Delete recipe.
    """
    if not current_user:
        return jsonify({'message': 'Permission is required'}), 403
    recipe = Recipe.query.filter(Recipe.id == recipe_id).filter(Recipe.user_id == current_user.id).first()

    if not recipe:
        return jsonify({'message': 'Recipe not found', 'status': False}), 404

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe deleted successfully', 'status': True}), 201
