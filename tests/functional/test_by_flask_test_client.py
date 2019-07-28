import unittest
import json

from app import app as tested_app


class TestApp(unittest.TestCase):
    def test_help(self):
        # creating a FlaskClient instance to interact with the app
        app = tested_app.test_client()

        # calling /api/ endpoint
        hello = app.get('/api/hello')

        # asserting the body
        body = json.loads(str(hello.data, 'utf8'))
        self.assertEqual(body['Hello'], 'Anonymous')


if __name__ == '__main__':
    unittest.main()