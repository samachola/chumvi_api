import json
from marshmallow import Schema, post_load, pre_load, validates, fields, ValidationError
from .models import User, Category, Recipe
from .helpers import special_character, email_exists, username_exists, check_password, check_mail

class UserSchema(Schema):
    """
    Validates Registration.
    """
    username = fields.String(required=True,
    error_messages={'required': 'Username must be at least 3 characters'})
    email = fields.Email(required=True)
    password = fields.String(required=True)

    @validates('username')
    def validate_username(self, username):
        if special_character(username):
            raise ValidationError('Username should not contain Special characters')
        if len(username) <= 3:
            raise ValidationError('Username should be atleast 4 characters long')
        elif username_exists(username):
            raise ValidationError('A user with username "%s" already exists' % username)

    @validates('email')
    def validate_user_exists(self, email):
        if email_exists(email):
            raise ValidationError('A user with email "%s" already exixts' % email)

    @validates('password')
    def validate_user_password(self, password):
        if not check_password(password):
            raise ValidationError('Password should be atleast 6 characters long with atleast one special, uppercase, lowercase and numeric character')
        
class LoginSchema(Schema):
    """Schema for validating login data."""
    email = fields.Email(required=True)
    password = fields.String(required=True)

    @validates('email')
    def validate_email(self, email):
        if not email_exists(email):
            raise ValidationError('User does not exists.')
        elif not check_mail(email):
            raise ValidationError('Please provide a valid email address')

class CategorySchema(Schema):
    """Schema for validating user's categories"""
    category_name = fields.String(required=True)
    category_description = fields.String(required=True)

    @validates('category_name')
    def validate_category_name(self, category_name):
        if special_character(category_name):
            raise ValidationError('Category name should not contain special characters')
        elif len(category_name) <= 4:
            raise ValidationError('Category name should be atleast 5 Characters')

class RecipeSchema(Schema):
    """Schema used for validating Recipes."""
    title = fields.String(required=True)
    ingredients = fields.String(required=True)
    steps = fields.String(required=True)
    category_id = fields.Integer(required=True)

    @validates('title')
    def validate_recipe_title(self, title):
        if special_character(title):
            raise ValidationError('Recipe title should not contain special characters')
        elif len(title) <= 3:
            raise ValidationError('Recipe title should more than 3 characters long')
    
    @validates('category_id')
    def validate_category_id(self, category_id):
        if type(category_id) != int:
            raise ValidationError('Category id should be an interger')
            
        
        
    
