from flask import request, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app import app, db, models
import re

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

def special_character(title):
      """Helper function that checks if item has a special character."""
      if re.findall('[^A-Za-z0-9 ]', title):
            return True
      else:
            return False

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