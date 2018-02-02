import json
from werkzeug.datastructures import Headers
from tests import ApiTestCase

class RecipeTestCase(ApiTestCase):
    def test_add_recipe(self):
        """Function tests if user can add a recipe."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1
        }

        response = self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Successfully added new Recipe', resp['message'])

    def test_add_recipe_with_special_char(self):
        """Function tests if user can add a recipe that contains special characters"""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maind!!% Choma', 
            'ingredients': 'Maindi, Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1,
            'user_id': 1
        }

        response = self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('Recipe title should not contain special characters', resp['errors']['title'])

    def test_add_recipe_without_title(self):
        """Function tests if user can add a recipe without title"""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': '', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1,
            'user_id': 1
        }

        response = self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('Recipe title should more than 3 characters long', resp['errors']['title'])

    def test_add_recipe_without_ingredients(self):
        """Function tests if user can add a recipe without ingredients"""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': '', 
            'steps':'Choma maindi',
            'category_id': 1,
            'user_id': 1
        }

        response = self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('We need ingredients that are more that 3 characters', resp['errors']['ingredients'])

    def test_add_recipe_without_steps(self):
        """Function tests if user can add a recipe without steps"""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'',
            'category_id': 1,
            'user_id': 1
        }

        response = self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('We need to cook something more that 3 characters', resp['errors']['steps'])

    def test_get_recipe(self):
        """Tests if user can see a sigle recipe."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1,
            'user_id': 1
        }
        self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        response = self.tester.get('/api-v0/recipe/1', content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('maindi choma', resp['recipe']['title'])
    
    def test_get_unexisting_recipe(self):
        """Tests if user can get an unexisting recipe."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        response = self.tester.get('/api-v0/recipe/1', content_type="application/json", headers=h)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Recipe is not available')

    def test_update_recipe(self):
        """Tests update recipe."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1
        }
        updated_items = {
            'title': 'Maindi Boilo', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1
        }
        self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        response = self.tester.put('/api-v0/recipe/1', data=json.dumps(updated_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Successfully updated recipe', resp['message'])
        self.assertEqual(updated_items['title'], resp['recipe']['title'])

    def test_update_recipe_with_empty_title(self):
        """Tests update recipe without a title."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1
        }
        updated_items = {
            'title': '', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1
        }
        self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        response = self.tester.put('/api-v0/recipe/1', data=json.dumps(updated_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('Recipe title should more than 3 characters long', resp['errors']['title'])

    
    def test_update_recipe_with_empty_ingredients(self):
        """Tests update recipe without a indgredients."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma', 
            'ingredients': 'Maindi Ndimu', 
            'steps':'Choma maindi',
            'category_id': 1,
            'user_id': 1
        }
        updated_items = {
            'title': 'Maindi', 
            'ingredients': '', 
            'steps':'Choma maindi',
            'category_id': 1,
            'user_id': 1
        }
        self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        response = self.tester.put('/api-v0/recipe/1', data=json.dumps(updated_items), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('We need ingredients that are more that 3 characters', resp['errors']['ingredients'])

    def test_delete_recipe(self):
        """Tests if user can delete a recipe."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        recipe_items = {
            'title': 'Maindi Choma',
            'ingredients': 'Maindi Ndimu',
            'steps': 'Choma Maindi',
            'category_id': 1,
            'user_id': 1
        }
        self.tester.post('/api-v0/recipe', data=json.dumps(recipe_items), content_type='application/json', headers=h)
        response = self.tester.delete('/api-v0/recipe/1', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Recipe deleted successfully', resp['message'])