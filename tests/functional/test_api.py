import unittest

from flask_webtest import TestApp

from app import app as tested_app


class TestMyApp(unittest.TestCase):
    def test_help(self):
        app = TestApp(tested_app)
        hello = app.get("/api")
        self.assertEqual(hello.json["Hello"], "World")


if __name__ == "__main__":
    unittest.main()
