from app import db

class User(db.Model):
    """This class represents the user table."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "Successfully added : {}".format(self.username)

class Category(db.Model):
    """This class represents the category table"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80))
    category_description = db.Column(db.String)
    user_id = db.Column(db.Integer)
    recipes = db.relationship('Recipe', order_by='Recipe.id', cascade="all, delete-orphan")

    def __init__(self, category_name, category_description, user_id):
        self.category_name = category_name
        self.category_description = category_description
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "Category: {}".format(self.category_name)

class Recipe(db.Model):
    """This class represents the Recipe table."""

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    ingredients = db.Column(db.String)
    steps = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    user_id = db.Column(db.Integer)

    def __init__(self, title, ingredients, steps, category_id, user_id):
        self.title = title
        self.ingredients = ingredients
        self.steps = steps
        self.category_id = category_id
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "Recipe: {}".format(self.title)