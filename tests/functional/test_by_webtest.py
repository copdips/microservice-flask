import os
import unittest


class TestMyApp(unittest.TestCase):
    def setUp(self):
        # if HTPP_SERVER is set, we use it as an endpoint
        http_server = os.environ.get("HTTP_SERVER")

        if http_server is not None:
            from webtest import TestApp

            self.app = TestApp(http_server)
        else:
            # fallbacks to the wsgi app
            from flask_webtest import TestApp
            from app import app

            self.app = TestApp(app)

    def test_help(self):
        hello = self.app.get("/api")
        self.assertEqual(hello.json["Hello"], "World!")


if __name__ == "__main__":
    unittest.main()
