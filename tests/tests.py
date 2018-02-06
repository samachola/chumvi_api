import jwt
import json
import unittest
from werkzeug.datastructures import Headers
import app
from app import app, db, models

User = models.User
Category = models.Category
Recipe = models.Recipe
class ApiTestCase(unittest.TestCase):  

    def setUp(self):
        self.tester = app.test_client(self)
        self.login_data = {'email': 'test@example.com', 'password': 'Osupportit.0'}
        self.category_data = {'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}
        self.registration_data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'Osupportit.0'}
        app.config.from_pyfile('testconf.cfg')        
        db.create_all()

    def register(self):
        """User registration helper"""
        return self.tester.post('/api-v0/auth/register', data=json.dumps(self.registration_data), content_type='application/json')
    
    def login(self):
        """User login helper."""
        return self.tester.post('/api-v0/auth/login/', data=json.dumps(self.login_data), content_type='application/json')
    
    def categories(self):
        """Add Categories helper."""
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        return self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)

    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()