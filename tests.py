from flask_testing import TestCase
import app
from app import app, db, User, Category, Recipe
import unittest
import json

class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_pyfile('testconf.cfg')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class ApiTestCase(BaseTestCase):

    def test_register(self):
        # user = User(username='achola', email='sam.achola@live.com', password='123456')
        # db.session.add(user)
        # db.session.commit()

        # # this works
        # assert user in db.session
        response = self.post('/auth/register', json({"username": "achola", "email": "sam.achola@live.com", "password": "123456"})
        self.assertEqual(response.status_code == 200)
        self.assertEqual(json_of_response(response) == {'message': 'Registration Successful'})

        #self.assertEqual(json.loads(response.get_data()), {'message': 'Registration Successful'})


    def json_of_response(response):
        """Decode json from response"""
        return json.loads(response.data.decode('utf8')) 

if __name__ == '__main__':
    unittest.main()