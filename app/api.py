from flask import request, make_response, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app import app, db, models

User = models.User
Category = models.Category
Recipe = models.Recipe

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Access Token unavailable', "status": False})

        try:
            data = jwt.decode(token, app.secret_key)
            current_user = User.query.filter_by(email=data['email']).first()
        except:
            return jsonify({'message': 'Invalid Token', "status": False}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], admin=False, password=hashed_password)
    new_user.save()

    return jsonify({'message': 'Registration Successful'})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data['email'] or not data['password']:
        return jsonify({'message': 'email and password is required'}), 401

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'User does not exists'}), 401
    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'email': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)}, app.secret_key)
        return jsonify({'message':'Login successful', 'token': token.decode('UTF-8'), 'status': True})

    return jsonify({'message': 'You provided an incorrect password'}), 401


@app.route('/auth/logout', methods=['POST'])
def logout():
    data = request.get_json()


    if not data:
        return jsonify({'message': 'something went wrong'})

    return jsonify({'message': 'user is logged out successfully'})

@app.route('/auth/reset-password', methods=['POST'])
def reset():
    data = request.get_json()

    if not data or not data['email']:
        return jsonify({'message': 'Email is required'})

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'Email does not exists'}), 401

    return jsonify({'message': 'A reset link has been sent to your email'})


@app.route('/category', methods=['POST'])
@token_required
def add_category(current_user):
    if not current_user:
        return jsonify({'messsage': 'Permission required', 'status': False})

    data = request.get_json()
    if not data or not data['category_name']:
        return jsonify({'message': 'Category name is required', 'status': False})

    new_category = Category(category_name=data['category_name'], category_description=data['category_description'], user_id=current_user.id)
    new_category.save()

    return jsonify({'message': 'Succefully added new category', 'status': True})


@app.route('/category', methods=['GET'])
@token_required
def get_categories(current_user):
    
    data = []
    categories = Category.query.filter_by(user_id=current_user.id).all()
    for cats in categories:
        cat = {}
        cat['id'] = cats.id
        cat['category_name'] = cats.category_name
        cat['category_description'] = cats.category_description
        data.append(cat)

    return jsonify({'categories': data})

@app.route('/category/<int:category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    
    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({'message': 'Category does not exist', 'status': False})

    cat = {}
    cat['id'] = category.id
    cat['category_name'] = category.category_name

    return jsonify({'category': cat})


@app.route('/category/<category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    data = request.get_json()
    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({'message': 'Category does not exist', 'status': False})

    if not data or not data['category_name']:
        return jsonify({'message': 'category name missing', 'status': False})

    category.category_name = data['category_name']
    db.session.commit()
    return jsonify({'message': 'Successfully updated category', 'status': True})


@app.route('/category/<category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({'message': 'Could not find category', 'status': False})

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category successfully deleted', 'status': True})
    

@app.route('/recipe', methods=['POST'])
@token_required
def add_recipe(current_user):

    data = request.get_json()

    if not data or not data['title'] or not data['ingredients'] or not data['steps'] or not data['category_id']:
        return jsonify({'message': 'all recipe fields are required', 'status': False})

    recipe = Recipe(title=data['title'], ingredients=data['ingredients'], steps=data['steps'], category_id=data['category_id'], user_id=current_user.id)
    recipe.save()

    return jsonify({'message': 'Successfully added new Recipe', 'status': True})


@app.route('/recipe', methods=['GET'])
@token_required
def get_recipes(current_user):

    output = []
    
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    if not recipes:
        return jsonify({'message': 'No recipes available'})
    for recipe in recipes:
        recipee = {}
        recipee['id'] = recipe.id
        recipee['title'] = recipe.title
        recipee['ingredients'] = recipe.ingredients
        recipee['steps'] = recipe.steps
        recipee['category_id'] = recipe.category_id
        recipee['user_id'] = recipe.user_id
        output.append(recipee)

    return jsonify({'recipes': output})


@app.route('/recipe/<recipe_id>', methods=['GET'])
@token_required
def get_recipe(current_user, recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe is not available', 'status': False})

    recipee = {}
    recipee['id'] = recipe.id
    recipee['title'] = recipe.title
    recipee['ingredients'] = recipe.ingredients
    recipee['steps'] = recipe.steps
    recipee['category_id'] = recipe.category_id
    recipee['user_id'] = recipe.user_id

    return jsonify({'recipe': recipee})

@app.route('/recipe/<recipe_id>', methods=['PUT'])
@token_required
def update_recipe(current_user, recipe_id):
    data = request.get_json()
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe is not available', 'status': False})

    recipe.title = data['title']
    recipe.ingredients = data['ingredients']
    recipe.step = data['steps']
    recipe.category_id = data['category_id']

    db.session.commit()
    return jsonify({'message': 'Successfully updated recipe', 'status': True})

@app.route('/recipe/<recipe_id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe not found', 'status': False})

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe deleted successfully', 'status': True})
