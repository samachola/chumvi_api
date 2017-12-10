from flask_testing import TestCase
import app
from app import app, db, models
import unittest
import json

User = models.User
Category = models.Category
Recipe = models.Recipe
    

class ApiTestCase(unittest.TestCase):
    

    def setUp(self):
        self.tester = app.test_client(self)
        app.config.from_pyfile('testconf.cfg')        
        db.create_all()


    def register(self):
        """User registration helper"""
        tester = app.test_client(self)
        return tester.post('/auth/register', data=json.dumps({"username": "achola", "email": "acholasam1@gmail.com", "password": "123456"}), content_type='application/json')
    
    def login(self):
        """User Login helper."""
        
    def test_registration(self):
        """Test user registration."""
        tester = app.test_client(self)
        response = tester.post('/auth/register', data=json.dumps({'username': 'achola', 'email': 'acholasam1@gmail.com', 'password': '123456'}), content_type='application/json')
        self.assertEqual(response.status_code, 200) 

    def test_login(self):
        """Test user login and authentication."""
        self.register()
        response = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': '123456'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_add_category(self):
        """Tests if user can add a new category."""
        self.register()
        self.login()
        token = self.login()
        response = self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), headers={'x-access-token': token['token']}, content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)        

    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()