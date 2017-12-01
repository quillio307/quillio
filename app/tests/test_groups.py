import unittest

from flask import current_app
from flask_mongoengine import MongoEngine
from flask_testing import TestCase

from app import app, db
from app.modules.auth.model import User
from app.modules.groups.model import Group


class TestGroups(TestCase):
    def create_app(self):
        app.config.from_object('config_test')
        db = MongoEngine(app)
        User.objects.all().delete()
        Group.objects.all().delete()
        return app

    def test_groups(self):
        self._test_group_setup()
        self._test_create_group()
        self._test_update_group()

    def _test_group_setup(self):
        # create dummy users
        self.client.post('/auth/signup', data=dict(
            name="Test",
            email="test@test.com",
            password="password"
        ))

        self.client.post('/auth/signup', data=dict(
            name="Test 1",
            email="test1@test.com",
            password="password"
        ))

        self.client.post('/auth/signup', data=dict(
            name="Test 2",
            email="test2@test.com",
            password="password"
        ))

        self.client.post('/auth/signup', data=dict(
            name="Test 3",
            email="test3@test.com",
            password="password"
        ))

        self.client.post('/auth/signup', data=dict(
            name="Test 4",
            email="test4@test.com",
            password="password"
        ))

        user = User.objects.get(email="test@test.com")
        user.authenticated = True
        user.save()

    def _test_create_group(self):
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Logged in Successfully', str(response.data))

        # create group
        response = self.client.post('/groups/create', data=dict(
            name="test group",
            emails="test1@test.com test2@test.com",
        ), follow_redirects=True)

        self.assertIn('New Group Created with', str(response.data))

    def _test_update_group(self):
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="password"
        ), follow_redirects=True) 

        self.assertIn('Logged in Successfully', str(response.data))

        try:
            group = Group.objects.get(name="test group")
        except Exception as e:
            print(e)
            self.assertTrue(False)
            return

        response = self.client.post('/groups/update', data=dict(
            name="test group update",
            description="testing group update",
            emails_to_add="test3@test.com",
            admin_emails_to_add="test4@test.com",
            emails_to_remove="test2@test.com",
            group_id=group.id
        ), follow_redirects=True)

        self.assertIn('Group Successfully Updated', str(response.data))

    def _test_delete_group(self):
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Logged in Successfully', str(response.data))

        try:
            group = Group.objects.get(name="test group update")
        except Exception as e:
            print(e)
            self.assertTrue(False)
            return

        response = self.client.post('/groups/delete', data=dict(
            group_id=str(group.id)
        ))

        self.assertIn('Group Successfully Deleted', str(response.data))
