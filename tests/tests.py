import app
from app import app, db, models
import unittest
import json
from werkzeug.datastructures import Headers
import jwt

User = models.User
Category = models.Category
Recipe = models.Recipe
    

class ApiTestCase(unittest.TestCase):  

    def setUp(self):
        self.tester = app.test_client(self)
        self.login_data = {'email': 'acholasam1@gmail.com', 'password': 'Osupportit.0'}
        app.config.from_pyfile('testconf.cfg')        
        db.create_all()


    def register(self):
        """User registration helper"""
        tester = app.test_client(self)
        return tester.post('/auth/register/', data=json.dumps({"username": "achola", "email": "acholasam1@gmail.com", "password": "Osupportit.0"}), content_type='application/json')
    def login(self):
        """User login helper."""
        return self.tester.post('/auth/login/', data=json.dumps(self.login_data), content_type='application/json')
    
    def categories(self):
        """Add Categories helper."""
        res = self.tester.post('/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        return self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)

        
    def test_registration(self):
        """Test user registration."""
        tester = app.test_client(self)
        response = tester.post('/auth/register/', data=json.dumps({'username': 'achola', 'email': 'acholasam1@gmail.com', 'password': 'Osupportit.0'}), content_type='application/json')
        self.assertEqual(response.status_code, 200) 

    def test_login(self):
        """Test user login and authentication."""
        self.register()
        response = self.tester.post('/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_add_category(self):
        """Tests if user can add a new category."""
        self.register()
        res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osupportit.0'}), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        
        response = self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), headers=h, content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)

    # def test_add_category_without_name(self):
    #     """Tests if category name validation is working"""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     response = self.tester.post('/category', data=json.dumps({'category_name': '', 'category_description': 'Awesome Breakfast'}), headers=h, content_type='application/json')
    #     data = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data['status'], False)
    #     self.assertEqual(data['message'], 'Category name is required')

    # def test_add_category_without_desc(self):
    #     """Tests if user can add category without a description."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     response = self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': ''}), content_type='application/json', headers=h)
    #     data = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data['status'], False)
    #     self.assertEqual(data['message'], 'Category description is required')


    # def test_get_category(self):
    #     """Tests if user can add a new category."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     response = self.tester.get('/category', headers=h)
    #     data = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Breakfast', data['categories'][0]['category_name'])

    # def test_edit_category(self):
    #     """Test edit category."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     response = self.tester.put('/category/1', data=json.dumps({'category_name': 'Dinner', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     resp = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Successfully updated category', resp['message'])

    # def test_edit_unexisting_category(self):
    #     """Tests if user can edit an unexisting category."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     response = self.tester.put('/category/23', data=json.dumps({'category_name': 'Dinner', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     resp = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Category does not exist', resp['message'])
    
    # def test_delete_category(self):
    #     """Tests if user can delete a category."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     response = self.tester.delete('/category/1', headers=h)
    #     resp = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(resp['message'], 'Category successfully deleted')
    #     self.assertEqual(resp['status'], True)

    # def test_delete_unexisting_category(self):
    #     """Tests if user can delete an unexisiting category."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     response = self.tester.delete('/category/2', headers=h)
    #     resp = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(resp['status'], False)
    #     self.assertEqual(resp['message'], 'Could not find category')


    # def test_add_recipe(self):
    #     """Function tests if user can add a recipe."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     recipe_items = {
    #         'title': 'Maindi Choma', 
    #         'ingredients': 'Maindi, Ndimu', 
    #         'steps':'Choma maindi',
    #         'category_id': 1,
    #         'user_id': 1
    #     }
    #     response = self.tester.post('/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
    #     resp = json.loads(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Successfully added new Recipe', resp['message'])

    # def test_view_single_recipe(self):
    #     """Tests view single recipe route."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     recipe_items = {
    #         'title': 'Maindi Choma', 
    #         'ingredients': 'Maindi, Ndimu', 
    #         'steps':'Choma maindi',
    #         'category_id': 1,
    #         'user_id': 1
    #     }
    #     updated_items = {
    #         'title': 'Maindi Boilo', 
    #         'ingredients': 'Maindi, Ndimu', 
    #         'steps':'Choma maindi',
    #         'category_id': 1,
    #         'user_id': 1
    #     }
    #     self.tester.post('/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
    #     response = self.tester.put('/recipe/1', data=json.dumps(updated_items), content_type='application/json', headers=h)
    #     resp = json.loads(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Successfully updated recipe', resp['message'])

    # def test_get_recipe(self):
    #     """Tests if user can see a sigle recipe."""
    #     self.register()
    #     res = self.tester.post('/auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     recipe_items = {
    #         'title': 'Maindi Choma', 
    #         'ingredients': 'Maindi, Ndimu', 
    #         'steps':'Choma maindi',
    #         'category_id': 1,
    #         'user_id': 1
    #     }
    #     self.tester.post('/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
    #     response = self.tester.get('/recipe/1', content_type='application/json', headers=h)
    #     resp = json.loads(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Maindi Choma', resp['recipe']['title'])

    # def test_delete_recipe(self):
    #     """Tests if user can delete a recipe."""
    #     self.register()
    #     res = self.tester.post('auth/login', data=json.dumps({'email': 'acholasam1@gmail.com', 'password': 'Osuport.2'}), content_type='application/json')
    #     data = json.loads(res.data)
    #     h = Headers()
    #     h.add('x-access-token', data['token'])
    #     self.tester.post('/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
    #     recipe_items = {
    #         'title': 'Maindi Choma',
    #         'ingredients': 'Maindi, Ndimu',
    #         'steps': 'Choma Maindi',
    #         'category_id': 1,
    #         'user_id': 1
    #     }
    #     self.tester.post('/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
    #     response = self.tester.delete('/recipe/1', headers=h)
    #     resp = json.loads(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual('Recipe deleted successfully', resp['message'])


    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()