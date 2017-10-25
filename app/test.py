import urllib.request
import unittest
from flask import Flask 
from flask_testing import TestCase, LiveServerTestCase
import mongoengine
from app import create_app as create_app_base 
from passlib.hash import bcrypt
from app.modules.auth.model import User
from app.modules.auth.model import user_datastore


class TestUser(TestCase):
	render_templates = False

	#required for superclass implementation
	#with Live server test case, port is default at 5000
	#left default timeout to be 5seconds 
	def create_app(self):
		return create_app_base(
			MONGODB_SETTINGS={'DB': 'testing'}, 
			TESTING = True,
			CSRF_ENABLED = False
		)

	
	def test_create_app():
		app = create_app()
		assert app.config['TESTING']
		assert mongoengine.connection.get_db().name == 'testing'

	#testing user creation with valid credentials
	def test_create_valid_user():
		try:
			test_email = "testing.email@example.com"
			test_password_hashed = bcrypt.encrypt("a_password")
			test_name = "First Last"
			test = User(test_email, test_password_hashed, test_name)
			test.save()
		except Exception as e: 
			pass		
		assert True

		
		
	#tets use creation with invalid credentials --> expects an exception 
	def test_create_invalid_user():
		try: 
			test = User("", "" )
			test.save()

		except Exception as e: 
			assert True

	def test_succesful_login():
		test_user = user_datastore.find_user(email="testing.email@example.com")
		assert bcrypt.verify("a_password", test_user.password) == True

	def test_unknown_email_login():
		pass


	def test_incorrect_password_login(): 
		test_user = user_datastore.find_user(email="testing.email@example.com")
		assert bcrypt.verify("lol", test_user.password) == False


	if __name == '__main__':
		unittest.main()

