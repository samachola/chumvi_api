import json
from tests import ApiTestCase

class AuthTestCase(ApiTestCase):
    def test_registration(self):
        """Test user registration."""
        response = self.tester.post('/api-v0/auth/register', data=json.dumps({'username': 'achola', 'email': 'acholasam1@gmail.com', 'password': 'Osupportit.0'}), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['username'], 'achola')

    def test_registering_duplicate_email(self):
        """Test if user can register with an existing email."""
        self.register()
        response = self.tester.post('/api-v0/auth/register', data=json.dumps({'username': 'achola', 'email': 'acholasam1@gmail.com', 'password': 'Osupportit.0'}), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('A user with email "%s" already exists' % 'acholasam1@gmail.com', data['errors']['email'])

    def test_registering_with_duplicate_username(self):
        """Tests if user can register with an existing username."""
        self.register()
        response = self.tester.post('/api-v0/auth/register', data=json.dumps({'username': 'achola', 'email': 'sam@example.org', 'password': 'Osupportit.0'}), content_type="application/json")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('A user with username "%s" already exists' % 'achola', data['errors']['username'])

    def test_username_contains_special_character(self):
        """Test if username contains special characters."""
        response = self.tester.post('/api-v0/auth/register', data=json.dumps({'username': 'achola#', 'email': 'sam@example.org', 'password': 'Osupportit.0'}), content_type="application/json")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertIn('Username should not contain Special characters', data['errors']['username'])
        
    def test_login(self):
        """Test user login and authentication."""
        self.register()
        response = self.tester.post('/api-v0/auth/login', data=json.dumps(self.login_data), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Login successful')
