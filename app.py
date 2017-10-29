from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    admin = db.Column(db.Boolean)
    password = db.Column(db.String(80))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50))

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    ingredients = db.Column(db.String)
    steps = db.Column(db.String)
    category_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

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
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'Invalid Token', "status": False}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], admin=False, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration Successful'})

@app.route('/auth/login', methods=['POST'])
def login():
    #auth = request.authorization
    data = request.get_json()

    if not data or not data['username'] or not data['password']:
        return jsonify({'message': 'username and password is required'}), 401

    # if not auth or not auth.username or auth.password:
    #     return make_response('Could not verify', 401, {'WWW-authenticate': 'Base realm="Login Required"'})

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'message': 'User does not exists'}), 401
    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)}, app.secret_key)
        return jsonify({'token': token.decode('UTF-8')})

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

    new_category = Category(category_name=data['category_name'])
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Succefully added new category', 'status': True})


@app.route('/category', methods=['GET'])
@token_required
def get_categories(current_user):
    
    data = []
    categories = Category.query.all()
    for cats in categories:
        cat = {}
        cat['id'] = cats.id
        cat['category_name'] = cats.category_name
        data.append(cat)

    return jsonify({'categories': data})

@app.route('/category/<category_id>', methods=['GET'])
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
    
    


  

if __name__ == '__main__':
    app.run(debug=True)