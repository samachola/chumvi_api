from flask import Blueprint, request, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app import app, db, models
import re
from flasgger import swag_from
from .helpers import token_required, check_password, check_mail, special_character

User = models.User

mod = Blueprint('auth', __name__)

@mod.route('/auth/register', methods=['POST'])
@swag_from('docs/auth_register.yml')
def register():
    """ 
    User Registration
    """
    data = request.get_json()

    if 'username' not in data:
        return jsonify({"message": "username key does not exist", 'status': False}), 403

    if 'email' not in data:
        return jsonify({"message": "email key does not exist", 'status': False}), 403

    if 'password' not in data:
        return jsonify({"message": "password key does not exist", 'status': False}), 403

    if not data['username'] or not data['email'] or data['email'].isspace() or data['username'].isspace() :
        return jsonify({"message": "All fields are required"}), 401

    if not check_mail(data['email']):
        return jsonify({"message": "Please provide a valid email", "status": False}), 401

    if special_character(data['username']):
        return jsonify({'message': 'Special characters are not allowed in username', 'status': False}),

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

    if special_character(data['username']):
          return jsonify({'message': 'username cannot contain special character'}), 401

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], admin=False, password=hashed_password)

    try:
      new_user.save()
    except:
      return jsonify({"message": "user already exists", "status": False}), 401

    return jsonify({'message': 'Registration Successful', 'status': True}), 201

@mod.route('/auth/login', methods=['POST'])
@swag_from('docs/auth_login.yml')
def login():
    data = request.get_json()
    if 'password' not in data:
        return jsonify({"message": "password key does not exist", 'status': False}), 403

    if 'email' not in data:
        return jsonify({"message": "email key does not exist", 'status': False}), 403

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
