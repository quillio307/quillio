import unittest

from flask import current_app
from flask_mongoengine import MongoEngine
from flask_testing import TestCase

from app import app, db
from app.modules.auth.model import User
from app.modules.meetings.model import Meeting


class TestMeetings(TestCase):
    def create_app(self):
        app.config.from_object('config_test')
        db = MongoEngine(app)
        User.objects.all().delete()
        Meeting.objects.all().delete()
        return app

    def test_meetings(self):
        self._test_setup()
        self._test_create_meeting()

    def _test_create_meeting(self):
        response = self.client.post('/auth/login', data=dict(
            email="test@test.com",
            password="password"
        ), follow_redirects=True)

        self.assertIn('Logged in Successfully', str(response.data))

        response = self.client.post('/meetings/create', data=dict(
            name="test meeting",
            emails="test1@test.com test2@test.com",
            nature="academic"
        ), follow_redirects=True)

        self.assertIn('New Meeting Created', str(response.data))

    def _test_setup(self):
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