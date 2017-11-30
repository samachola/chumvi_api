from flask_testing import TestCase
import app
from app import app, db, User, Category, Recipe
import unittest
import json

class BaseTestCase(unittest.TestCase):
    def create_app(self):
        app.config.from_pyfile('testconf.cfg')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class ApiTestCase(BaseTestCase):
    def test_registration(self):
        # user = User(username="achola", email="sam.achola@live.com", password="123456")
        tester = app.test_client(self)
        response = tester.get('/auth/register', data=json.dumps({"username": "achola", "email": "sam.achola@live.com", "password": "123456"}))
        self.assertEqual(response.status_code, 200)
    
    def test_category(self):
        tester = app.test_client(self)
        response = tester.get('/category', content_type='application/json')
        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main()