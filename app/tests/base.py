from flask_testing import TestCase

from app import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config_test')
        db.init_app(app)
        return app

    def test_connection(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
