import datetime
import jwt
from json.decoder import JSONDecodeError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify, make_response, json, url_for
from flask_mail import Mail, Message 
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from app import app, db, models

from flasgger import swag_from
from .helpers import token_required, check_password, check_mail, special_character, password_match
from .serializers import UserSchema, LoginSchema
from .models import User

mod = Blueprint('auth', __name__)
mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)

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
        return jsonify({'errors':'Missing keys'}), 422

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

    return jsonify({
        'errors': { 'password': 'You provided an incorrect password'}, 
        'message': 'You provided an incorrect password'}), 422

@mod.route('/auth/forgot_password', methods=['POST'])
@swag_from('docs/auth_reset.yml')
def forgot_password():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if user:
        token = serializer.dumps(user.email, salt='reset_salt')

        msg = Message('Chumvi: Reset password', sender='chumvi.api@gmail.com', recipients=[data['email']])
        # link = url_for('auth.reset_password', token=token, _external=True)
        link = 'https://chumvi-react.herokuapp.com/reset_password/{}'.format(token)
        msg.body = 'Click on the link to reset password {}'.format(link)
                    
        mail.send(msg)       
        return jsonify({'message': 'An email with a reset password link has been sent to {}'.format(data['email'])}), 200

    return jsonify({'message': 'User does not exists', 'status': False}), 404

@mod.route('/auth/reset_password/<token>', methods=['POST'])
@swag_from('docs/auth_reset_password.yml')
def reset_password(token):
    data = request.get_json()
    try:
        email = serializer.loads(token,  salt='reset_salt', max_age=180)
    except SignatureExpired:
        return jsonify({'message': 'Reset password token already expired', 'status': False}), 403
    except BadSignature:
        return jsonify({'message': 'Invalid Token', 'status': False }), 422
    user = User.query.filter_by(email=email).first()
    
    if not password_match(data['password'], data['confirm_password']):
        return jsonify({'message': 'Passwords do not match', 'status': False }), 422

    hashed_password = generate_password_hash(data['password'], method='sha256')
    user.password = hashed_password
    user.save()

    return jsonify({'message': 'Successfully reset password', 'status': True}), 201
