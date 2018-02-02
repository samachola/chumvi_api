import datetime
import jwt
from json.decoder import JSONDecodeError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify, make_response, json

from app import app, db, models

from flasgger import swag_from
from .helpers import token_required, check_password, check_mail, special_character
from .serializers import UserSchema, LoginSchema
from .models import User

mod = Blueprint('auth', __name__)

@mod.route('/auth/register', methods=['POST'])
@swag_from('docs/auth_register.yml')
def register():
    """ 
    User Registration
    """
    data = request.get_json()

    schema = UserSchema()
    try:
        user, errors = schema.loads(request.data)
    except JSONDecodeError:
        # response for no data/invalid data
        return jsonify({'error':'Missing keys'}), 422

    if errors:
        return make_response(json.dumps({'errors': errors}), 422)
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    new_user.save()

    return make_response(json.dumps(user)), 201

@mod.route('/auth/login', methods=['POST'])
@swag_from('docs/auth_login.yml')
def login():
    data = request.get_json()

    schema = LoginSchema()
    
    try:
        auth_user, errors = schema.loads(request.data)
    except JSONDecodeError:
        return jsonify({'message': 'Missing keys'}), 422

    if errors:
        return make_response(json.dumps({'errors': errors})), 422

    user = User.query.filter_by(email=data['email']).first()
    
    if check_password_hash(user.password, data['password']):
        token = jwt.encode(
            {
                'email': user.email, 
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=48)
            }, app.secret_key)

        return jsonify(
                {
                    'message':'Login successful',
                    'token': token.decode('UTF-8'),
                    'status': True}
                ), 200

    return jsonify({'message': 'You provided an incorrect password'}), 422
