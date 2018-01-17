from flask import Blueprint, request, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app import app, db, models
import re
from flasgger import Swagger
from .helpers import token_required, check_password, check_mail, special_character, category_exists

User = models.User
Category = models.Category

mod = Blueprint('categories', __name__)


@mod.route('/category', methods=['POST'])
@token_required
def add_category(current_user):
    """Add recipe categories. 
    ---
    tags:
      - Category
    parameters:
      - in: body
        name: body
        required: true
        type: object
        description: Add a new category
        schema:
          id: category
          type: object
          properties:
            category_name:
              type: string
              default: Dessert
            category_description:
              type: string
              default: Oh ye o' sweet tooth
      - in: header
        name: x-access-token
        required: true
        type: string
        description: x-access-token
        schema:
          properties:
            x-access-token:
              type: string
    responses:
      200:
        description: Succefully added new category
        schema:
          properties:
            status:
              type: boolean
              default: true
            message:
               type: string
               default: Succefully added new category      
    """
    if not current_user:
        return jsonify({'message': 'Permission required', 'status': False}), 401

    data = request.get_json()

    if 'category_name' not in data:
        return jsonify({'message':'category_name key not found in data', 'status': False }), 403

    if 'category_description' not in data:
        return jsonify({'message': 'category_description key not found in data', 'status': False }), 403

    if not data or not data['category_name'] or data['category_name'].isspace():
          return jsonify({'message': 'Category name is required', 'status': False}), 422

    if special_character(data['category_name']) or special_character(data['category_description']):
          return jsonify({'message': 'Category name and Description should not contain special characters', 'status': False}), 401

    if not data['category_description'] or data['category_description'].isspace():
          return jsonify({'message': 'Category description is required', 'status': False}), 422

    if category_exists(data['category_name']):
          return jsonify({'message': 'category already exists', 'status': False}), 400
    
    new_category = Category(category_name=data['category_name'], category_description=data['category_description'], user_id=current_user.id)
    new_category.save()

    return jsonify({'message': 'Succefully added new category', 'status': True}), 201


@mod.route('/category', methods=['GET'])
@token_required
def get_categories(current_user):
    """Get all user categories.
    ---
    tags:
      - Category
    parameters:
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
    """
    if not current_user:
          return jsonify({'message': 'Permision required'}), 401
    data = []
    categories = Category.query.filter_by(user_id=current_user.id).all()
    for cats in categories:
        cat = {}
        cat['id'] = cats.id
        cat['category_name'] = cats.category_name
        cat['category_description'] = cats.category_description
        data.append(cat)

    return jsonify({'categories': data}), 200

@mod.route('/category/<int:category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    """Get category by id.
    ---
    tags:
      - Category
    parameters:
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
      - in: path
        name: category_id
        type: integer
        required: true
        description: category id
    """
    
    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({'message': 'Category does not exist', 'status': False}), 404

    cat = {}
    cat['id'] = category.id
    cat['category_name'] = category.category_name
    cat['category_description'] = category.category_description

    return jsonify({'category': cat})


@mod.route('/category/<category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    """Update category by id.
    ---
    tags:
      - Category
    parameters:
      - in: body
        name: body
        required: true
        type: object
        description: Edit category
        schema:
          id: category
          type: object
          properties:
            category_name:
              type: string
              default: Dessert
            category_description:
              type: string
              default: Oh ye o' sweet tooth
        
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
      - in: path
        name: category_id
        type: integer
        required: true
        description: category id
    """
    if not current_user:
          return jsonify({'message': 'Permission required'}), 401
    data = request.get_json()
    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({'message': 'Category does not exist', 'status': False}), 404

    if 'category_name' not in data:
        return jsonify({'message': 'category_name key not found in data', 'status': False }), 403
    if 'category_description' not in data:
        return jsonify({'message': 'category_description key not found in data', 'status': False }), 403

    if not data or not data['category_name'] or data['category_name'].isspace():
        return jsonify({'message': 'category name missing', 'status': False}), 401
    
    if not data['category_description'] or data['category_description'].isspace():
        return jsonify({'message': 'category name missing', 'status': False}), 401

    if special_character(data['category_name']) or special_character(data['category_description']):
          return jsonify({'message': 'Category name and Description should not contain special characters', 'status': False}), 401


    category.category_name = data['category_name']
    category.category_description = data['category_description']
    db.session.commit()
    return jsonify({'message': 'Successfully updated category', 'status': True}), 202


@mod.route('/category/<category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    """Delete category by id.
    ---
    tags:
      - Category
    parameters:
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
      - in: path
        name: category_id
        type: integer
        required: true
        description: category id
    """ 
    if not current_user:
          return jsonify({'message': 'Permission required'}), 401
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({'message': 'Could not find category', 'status': False}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category successfully deleted', 'status': True}), 200

