from flask import request, make_response, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app import app, db, models
import re
from flasgger import Swagger
from sqlalchemy import or_

swagger = Swagger(app, 
        template={
            "consumes":[
                "application/json"
            ],
            "produces":[
                "application/json"
            ],
            "Accept":[
                "application/json"
            ]
        }
)

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
            return jsonify({'message': 'Access Token unavailable', "status": False}), 401

        try:
            data = jwt.decode(token, app.secret_key)
            current_user = User.query.filter_by(email=data['email']).first()
        except:
            return jsonify({'message': 'Invalid Token', "status": False}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/auth/register/', methods=['POST'])
def register():
    """ User Registration
    Register a user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        type: object
        description: New user details
        schema:
          type: object
          id: userreg
          properties:
            username:
              type: string
              default: achola
            email:
              type: string
              default: sam.achola@live.com
            password:
              type: string
              default: "123456"
    responses:
      200:
        description: Registration Successful
        schema:
          properties:
            message:
              type: string
              default: Registration Successful'
            status:
              type: boolean
              default: True
    """
    data = request.get_json()

    if not data['username'] or not data['email'] or data['email'].isspace() or data['username'].isspace() :
        return jsonify({"message": "All fields are required"}), 401
    if not check_mail(data['email']):
        return jsonify({"message": "Please provide a valid email", "status": False}), 401
    if not check_password(data['password']):
        return jsonify({
                        "message": "Password should contain atleast one uppercase character, one special character and one lowercase character",
                        "status": False 
                        }), 422
    email_exists = User.query.filter_by(email=data['email']).first()
    if email_exists:
          return jsonify({"message": "user with the same email already exists", "status": False}), 403
    username_exists = User.query.filter_by(username=data['username']).first()
    if username_exists:
          return jsonify({'message': 'A user with the same username already exists', 'status': False}), 403

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], admin=False, password=hashed_password)
    try:
      new_user.save()
    except:
      return jsonify({"message": "user already exists", "status": False}), 401

    return jsonify({'message': 'Registration Successful', 'status': True}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    """ User Login
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        type: object
        description: User details for login
        schema:
          id: user
          type: object
          properties:
            email:
              type: string
              default: sam.achola@live.com
            password:
              type: string
              default: "123456"
    responses:
      200:
        description: Login successful
        schema:
          properties:
            message:
              type: string
              default: Login successful
            status:
              type: boolean
              default: true
            token:
              type: string
              default: "[token]"
    """
    data = request.get_json()

    if not data or not data['email'] or not data['password'] or data['email'].isspace() or data['password'].isspace():
       return jsonify({'message': 'email and password is required'}), 401
    if not check_mail(data['email']):
        return jsonify({'message': 'Please provide a valid email address', 'status': False}), 422

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User does not exists'}), 401
    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'email': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=48)}, app.secret_key)
        return jsonify({'message':'Login successful', 'token': token.decode('UTF-8'), 'status': True}), 200

    return jsonify({'message': 'You provided an incorrect password'}), 401

@app.route('/auth/reset-password', methods=['POST'])
def reset():
    data = request.get_json()

    if not data or not data['email']:
        return jsonify({'message': 'Email is required'}), 422

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'Email does not exists'}), 400

    return jsonify({'message': 'A reset link has been sent to your email'})


@app.route('/category', methods=['POST'])
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
    if not data or not data['category_name'] or data['category_name'].isspace():
        return jsonify({'message': 'Category name is required', 'status': False}), 422
    if not data['category_description'] or data['category_description'].isspace():
        return jsonify({'message': 'Category description is required', 'status': False}), 422
    if category_exists(data['category_name']):
          return jsonify({'message': 'category already exists'}), 400

    new_category = Category(category_name=data['category_name'], category_description=data['category_description'], user_id=current_user.id)
    new_category.save()

    return jsonify({'message': 'Succefully added new category', 'status': True})


@app.route('/category', methods=['GET'])
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
        return jsonify({'message': 'Category does not exist', 'status': False})

    cat = {}
    cat['id'] = category.id
    cat['category_name'] = category.category_name
    cat['category_description'] = category.category_description

    return jsonify({'category': cat})


@app.route('/category/<category_id>', methods=['PUT'])
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
    data = request.get_json()
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({'message': 'Category does not exist', 'status': False})

    if not data or not data['category_name']:
        return jsonify({'message': 'category name missing', 'status': False})

    category.category_name = data['category_name']
    category.category_description = data['category_description']
    db.session.commit()
    return jsonify({'message': 'Successfully updated category', 'status': True})


@app.route('/category/<category_id>', methods=['DELETE'])
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
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({'message': 'Could not find category', 'status': False}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category successfully deleted', 'status': True})
    

@app.route('/recipe', methods=['POST'])
@token_required
def add_recipe(current_user):
    """Post a new recipe. 
    ---
    tags:
      - Recipe
    parameters:
      - in: body
        name: body
        required: true
        type: object
        description: Add a new recipe
        schema:
          id: recipe
          type: object
          properties:
            title:
              type: string
              default: Maindi
            ingredients:
              type: string
              default: Maize, Chilli powder
            steps:
              type: string
              default: Grill Maize, add chilli, enjoy
            category_id:
              type: integer
              default: 1
            
      - in: header
        name: x-access-token
        required: true
        type: string
        description: x-access-token
    responses:
      200:
        description: Successfully added new Recipe
        schema:
          properties:
            status:
              type: boolean
              default: true
            message:
               type: string
               default: Successfully added new Recipe      
    """

    data = request.get_json()

    if not data or not data['title'] or not data['ingredients'] or not data['steps'] or not data['category_id']:
        return jsonify({'message': 'all recipe fields are required', 'status': False}), 401
    if data['title'].isspace() or data['ingredients'].isspace() or data['steps'].isspace():
        return jsonify({'message': 'all recipe fields are required', 'status': False}), 401      
    if recipe_exists(data['title']):
          return jsonify({'message': 'Recipe already exists', 'status': False}), 401
    recipe = Recipe(title=data['title'], ingredients=data['ingredients'], steps=data['steps'], category_id=data['category_id'], user_id=current_user.id)
    recipe.save()

    return jsonify({'message': 'Successfully added new Recipe', 'status': True})


@app.route('/recipe', methods=['GET'])
@token_required
def get_recipes(current_user):
    """Get all user's recipes.
    ---
    tags:
      - Recipe
    parameters:
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
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
                recipee['user_id'] = recipe.user_id
                output.append(recipee)
    else:
        for recipe in recipes.items: 
            recipee = {}
            recipee['id'] = recipe.id
            recipee['title'] = recipe.title
            recipee['ingredients'] = recipe.ingredients
            recipee['steps'] = recipe.steps
            recipee['category_id'] = recipe.category_id
            recipee['user_id'] = recipe.user_id
            output.append(recipee)
            
    if output:
        return jsonify({'recipes': output})
    else:
        return jsonify({"message": "No recipes found"})


@app.route('/recipe/<recipe_id>', methods=['GET'])
@token_required
def get_recipe(current_user, recipe_id):
    """Get recipe by id.
    ---
    tags:
      - Recipe
    parameters:
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
      - in: path
        name: recipe_id
        type: integer
        required: true
        description: recipe id
    """
    recipe = Recipe.query.filter(Recipe.user_id == current_user.id).filter(Recipe.id == recipe_id).first()

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
    """Edit recipe by id. 
    ---
    tags:
      - Recipe
    parameters:
      - in: body
        name: body
        required: true
        type: object
        description: Edit a recipe
        schema:
          id: recipe
          type: object
          properties:
            title:
              type: string
              default: Maindi
            ingredients:
              type: string
              default: Maize, Chilli powder
            steps:
              type: string
              default: Boil Maize, add chilli, enjoy
            category_id:
              type: integer
              default: 1
            
      - in: header
        name: x-access-token
        required: true
        type: string
        description: x-access-token
      - in: path
        name: recipe_id
        type: integer
        required: true
        description: recipe id
        
    responses:
      200:
        description: Successfully updated recipe
        schema:
          properties:
            status:
              type: boolean
              default: true
            message:
               type: string
               default: Successfully updated recipe      
    """
    data = request.get_json()
    recipe = Recipe.query.filter(Recipe.user_id == current_user.id).filter(Recipe.id == recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe is not available', 'status': False})
    if data['title'].isspace():
        return jsonify({'message': 'Title is empty'})
    if data['ingredients'].isspace():
        return jsonify({'message': 'Recipe ingredients are required'})
    if data['steps'].isspace():
        return jsonify({'message': 'yo! we can\'t cook nothing!'})

    recipe.title = data['title']
    recipe.ingredients = data['ingredients']
    recipe.step = data['steps']
    recipe.category_id = data['category_id']

    db.session.commit()
    return jsonify({'message': 'Successfully updated recipe', 'status': True})

@app.route('/recipe/<recipe_id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, recipe_id):
    """Delete recipe.
    ---
    tags:
      - Recipe
    parameters:
      - in: header
        name: x-access-token
        type: string
        required: true
        description: x-access-token
      - in: path
        name: recipe_id
        type: integer
        required: true
        description: recipe id
    """
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({'message': 'Recipe not found', 'status': False})

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe deleted successfully', 'status': True})

def check_mail(user_email):
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', user_email)

    if match == None:
        return False
    else:
        return True

def check_password(user_password):
    """Check if a password is strong"""
    match = re.match('^(?=.*[a-z])(?=.*\d)(?=.*[A-Z])(?:.{6,})$', user_password)

    if match == None:
        return False
    else:
        return True

def recipe_exists(title):
  """Helper functions to check if a recipe already exists."""
  recipe = Recipe.query.filter_by(title=title).first()
  if recipe:
    return True
  else: 
    return False

def category_exists(title):
      """Helper functions to check if a recipe already exists."""
      recipe = Category.query.filter_by(category_name=title).first()
      if recipe:
        return True
      else: 
        return False