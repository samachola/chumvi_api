from flask import Blueprint, request, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app import app, db, models
import re
from flasgger import swag_from
from .helpers import token_required, check_password, check_mail, special_character, recipe_exists, category_exists

User = models.User
Recipe = models.Recipe
Category = models.Category

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
    if 'title' not in data or 'ingredients' not in data or 'steps' not in data or 'category_id' not in data:
          return jsonify({'message': 'All keys are required.', 'status': False}), 403

    if not data or not data['title'] or not data['ingredients'] or not data['steps'] or not data['category_id']:
        return jsonify({'message': 'all recipe fields are required', 'status': False}), 401

    if data['title'].isspace() or data['ingredients'].isspace() or data['steps'].isspace():
        return jsonify({'message': 'all recipe fields are required', 'status': False}), 401   

    if recipe_exists(data['title']):
        return jsonify({'message': 'Recipe already exists', 'status': False}), 401

    if special_character(data['title']) or special_character(data['ingredients']) or special_character(data['steps']):
        return jsonify({'message': 'Recipe info should not contain special characters', 'status': False }), 401
        
    recipe = Recipe(title=data['title'], ingredients=data['ingredients'], steps=data['steps'], category_id=data['category_id'], user_id=current_user.id)
    recipe.save()

    return jsonify({'message': 'Successfully added new Recipe', 'status': True}), 201


@mod.route('/recipe', methods=['GET'])
@token_required
@swag_from('docs/recipe_get_all.yml')
def get_recipes(current_user):
    """
      Get all user's recipes.
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    q = str(request.args.get('q','')).lower()

    output = []
    recipes = Recipe.query.filter_by(user_id=current_user.id).paginate(page = page, per_page = per_page)
           
    if not recipes:
        return jsonify({'message': 'No recipes available'})
    if q:
        for recipe in recipes.items: 
            if q.lower() in recipe.title.lower() or q.lower() in recipe.ingredients.lower() or q.lower() in recipe.steps.lower() :  
                recipee = {}
                recipee['id'] = recipe.id
                recipee['title'] = recipe.title
                recipee['ingredients'] = recipe.ingredients
                recipee['steps'] = recipe.steps
                recipee['category_id'] = recipe.category_id
                output.append(recipee)
    else:
        for recipe in recipes.items: 
            recipee = {}
            recipee['id'] = recipe.id
            recipee['title'] = recipe.title
            recipee['ingredients'] = recipe.ingredients
            recipee['steps'] = recipe.steps
            recipee['category_id'] = recipe.category_id
            output.append(recipee)
            
    if output:
        return jsonify({'recipes': output})
    else:
        return jsonify({"message": "No recipes found"})


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
    """Edit recipe by id. 
         
    """
    data = request.get_json()
    recipe = Recipe.query.filter(Recipe.user_id == current_user.id).filter(Recipe.id == recipe_id).first()

    if 'title' not in data or 'ingredients' not in data or 'steps' not in data or 'category_id' not in data:
          return jsonify({'message': 'All keys are required.', 'status': False}), 403

    if not recipe:
        return jsonify({'message': 'Recipe is not available', 'status': False}), 404
    if data['title'].isspace() or not data['title']:
        return jsonify({'message': 'Title is required'}), 401
    if data['ingredients'].isspace() or not data['ingredients']:
        return jsonify({'message': 'Recipe ingredients are required'}), 401
    if data['steps'].isspace() or not data['steps'] :
        return jsonify({'message': 'yo! we can\'t cook nothing!'}), 401
    if special_character(data['title']) or special_character(data['ingredients']) or special_character(data['steps']):
          return jsonify({'message': 'Special characters are not allowed'}), 401

    recipe.title = data['title']
    recipe.ingredients = data['ingredients']
    recipe.step = data['steps']
    recipe.category_id = data['category_id']

    db.session.commit()
    return jsonify({'message': 'Successfully updated recipe', 'status': True}), 201

@mod.route('/recipe/<recipe_id>', methods=['DELETE'])
@token_required
@swag_from('docs/recipe_delete.yml')
def delete_recipe(current_user, recipe_id):
    """
    Delete recipe.
    """
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe not found', 'status': False}), 4040

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe deleted successfully', 'status': True}), 201
