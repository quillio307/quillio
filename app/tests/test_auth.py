import unittest

from flask import current_app
from flask_mongoengine import MongoEngine
from flask_testing import TestCase

from app import app, db
from app.modules.auth.model import User


class TestAuthentication(TestCase):
    def create_app(self):
        app.config.from_object('config_test')
        db = MongoEngine(app)
        User.objects.all().delete()
        return app

    def test_connection(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_auth(self):
        self._test_signup()
        self._test_login()

    def _test_signup(self):
        # create account
        response = self.client.post('/auth/signup', data=dict(
            name="Test User",
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Activation Request', str(response.data))

        # account already exists
        response = self.client.post('/auth/signup', data=dict(
            name="Test User",
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('An Account Is Already Using', str(response.data))

    def _test_login(self):
        # invalid email
        response = self.client.post('/auth/login', data=dict(
            email="unknown@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Please Make Sure You Have Created an Account', str(response.data))

        # invalid password
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="invalid"
        ), follow_redirects=True)

        self.assertIn('Invalid Email or Password', str(response.data))

        # before authentication
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Please Authenticate Your Account', str(response.data))

        try:
            user = User.objects.get(email="test@test.com")
            user.authenticated = True
            user.save()
        except Exception as e:
            print(str(e))

        # send good request
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Logged in Successfully', str(response.data))


if __name__ == '__main__':
    unittest.main()
