import json
from json.decoder import JSONDecodeError
from flask import Blueprint, request, jsonify, make_response
from flasgger import swag_from
from app import db

from .helpers import token_required, check_password, check_mail, special_character, category_exists
from .models import User, Category
from .serializers import CategorySchema


mod = Blueprint('categories', __name__)

@mod.route('/category', methods=['POST'])
@token_required
@swag_from('docs/category_post.yml')
def add_category(current_user):
    """
    Add recipe categories.     
    """ 
    if not current_user:
        return jsonify({'message': 'Permission required', 'status': False}), 403

    data = request.get_json()
    schema = CategorySchema()

    try:
        category, errors = schema.loads(request.data)
    except JSONDecodeError:
        return jsonify({'message': 'Missing keys'}), 422
    if errors:
        return make_response(json.dumps({'errors': errors, 'status': False})), 422

    cat_exists = Category.query.filter(Category.category_name == data['category_name'].lower()).filter(Category.user_id == current_user.id).first()
    if cat_exists:
        return jsonify({
                            'message': 'Sorry, Category already exists',
                            'status': False
                       }), 406

    new_category = Category(category_name=data['category_name'].lower(),
                            category_description=data['category_description'],
                            user_id=current_user.id)
  
    new_category.save()
    return jsonify({'message': 'Succefully added new category', 'status': True, 'category': category}), 201

@mod.route('/category', methods=['GET'])
@token_required
@swag_from('docs/category_get_all.yml')
def get_categories(current_user):
    """
    Get all user categories.
    """
    if not current_user:
          return jsonify({'message': 'Permision required'}), 403
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
@swag_from('docs/category_get_id.yml')
def get_category(current_user, category_id):
    """
    Get category by id.
    """
    category = Category.query.filter(Category.id == category_id).filter(Category.user_id == current_user.id).first()

    if not category:
        return jsonify({'message': 'Category does not exist', 'status': False}), 404

    cat = {}
    cat['id'] = category.id
    cat['category_name'] = category.category_name
    cat['category_description'] = category.category_description

    return jsonify({'category': cat}), 200


@mod.route('/category/<category_id>', methods=['PUT'])
@token_required
@swag_from('docs/category_put.yml')
def update_category(current_user, category_id):
    """
    Update category by id.
    """
    if not current_user:
          return jsonify({'message': 'Permission required'}), 401
    data = request.get_json()
    schema = CategorySchema()

    try:
        category, errors = schema.loads(request.data)
    except JSONDecodeError:
        return jsonify({'message': 'Missing keys'}), 422
    if errors:
        return make_response(json.dumps({'errors': errors, 'status': False})), 422

    my_category = Category.query.filter(Category.id == category_id).filter(Category.user_id == current_user.id).first()
    if not my_category:
        return jsonify({'message': 'Category does not exist', 'status': False}), 404

    my_category.category_name = data['category_name'].lower()
    my_category.category_description = data['category_description']
    db.session.commit()
    return jsonify({'message': 'Successfully updated category', 'status': True, 'category': category }), 201


@mod.route('/category/<category_id>', methods=['DELETE'])
@token_required
@swag_from('docs/category_delete.yml') 
def delete_category(current_user, category_id):
    """
    Delete category by id.
    """ 
    if not current_user:
        return jsonify({'message': 'Permission required'}), 401
    category = Category.query.filter(Category.id == category_id).filter(Category.user_id == current_user.id).first()
    if not category:
        return jsonify({'message': 'Could not find category', 'status': False}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category successfully deleted', 'status': True}), 200

