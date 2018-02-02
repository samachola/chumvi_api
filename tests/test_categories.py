import json
from werkzeug.datastructures import Headers
from tests import ApiTestCase

class CategoryTestCase(ApiTestCase):
    def test_add_category(self):
        """Tests if user can add a new category."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        
        response = self.tester.post('/api-v0/category', data=json.dumps(self.category_data), headers=h, content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], True)
        self.assertEqual(data['message'], 'Succefully added new category')
        self.assertEqual(data['category']['category_name'], self.category_data['category_name'])

    def test_add_category_without_name(self):
        """ Tests if category name validation is working"""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        response = self.tester.post('/api-v0/category', data=json.dumps({'category_name': '', 'category_description': 'Awesome Breakfast'}), headers=h, content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['status'], False)
        self.assertIn('Category name should be atleast 5 Characters', data['errors']['category_name'])

    def test_add_category_with_special_char(self):
        """ Tests if user can add a category with speacial characters"""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        response = self.tester.post('/api-v0/category', data=json.dumps({'category_name': 'NewC@t3#fy11', 'category_description': 'Awesome Breakfast'}), headers=h, content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['status'], False)
        self.assertIn('Category name should not contain special characters', data['errors']['category_name'])

    def test_add_category_without_desc(self):
        """Tests if user can add category without a description."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        response = self.tester.post('/api-v0/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': ''}), content_type='application/json', headers=h)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['status'], False)
        self.assertIn('Category description should be atleast 5 Characters', data['errors']['category_description'])
    
    def test_duplicate_categories(self):
        """Tests if users can add duplicate categories."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)

        response = self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 406)
        self.assertEqual(data['status'], False)
        self.assertEqual(data['message'], 'Sorry, Category already exists')


    def test_get_category(self):
        """Tests if user can get a new category."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps({'category_name': 'Breakfast', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
        response = self.tester.get('/api-v0/category', headers=h)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual('breakfast', data['categories'][0]['category_name'])

    def test_edit_category(self):
        """Test edit category."""
        self.register()

        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])

        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        response = self.tester.put('/api-v0/category/1', data=json.dumps({'category_name': 'Dinner', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
        resp = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Successfully updated category', resp['message'])
        self.assertEquals('Dinner', resp['category']['category_name'])

    def test_edit_unexisting_category(self):
        """Tests if user can edit an unexisting category."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        response = self.tester.put('/api-v0/category/23', data=json.dumps({'category_name': 'Dinner', 'category_description': 'Awesome Breakfast'}), content_type='application/json', headers=h)
        resp = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertEqual('Category does not exist', resp['message'])
    
    def test_delete_category(self):
        """Tests if user can delete a category."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        self.tester.post('/api-v0/category', data=json.dumps(self.category_data), content_type='application/json', headers=h)
        
        response = self.tester.delete('/api-v0/category/1', content_type='application/json', headers=h)
        resp = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp['message'], 'Category successfully deleted')
        self.assertEqual(resp['status'], True)

    def test_delete_unexisting_category(self):
        """Tests if user can delete an unexisiting category."""
        self.register()
        res = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(res.data)
        h = Headers()
        h.add('x-access-token', data['token'])
        response = self.tester.delete('/api-v0/category/38', headers=h)
        resp = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(resp['status'], False)
        self.assertEqual(resp['message'], 'Could not find category')
