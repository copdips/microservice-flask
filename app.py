import time

from flask import Flask, Response, abort, g, jsonify, request, request_finished
from flask.signals import signals_available
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, ReadTimeout
from werkzeug.exceptions import HTTPException, default_exceptions
from werkzeug.routing import BaseConverter, ValidationError

from config import prod_settings
from teams import teams

if not signals_available:
    raise RuntimeError("pip install blinker")


def _time2etag(stamp=None):
    # epoch time format
    if stamp is None:
        stamp = time.time()
    return str(int(stamp * 1000))


_USERS = {
    "1": {"name": "Tarek", "modified": _time2etag()},
    "2": {"name": "Freya", "modified": _time2etag()},
}

_IDS = {tuple(val): id for id, val in _USERS.items()}


class RegisteredUser(BaseConverter):
    def to_python(self, value):
        if value in _USERS:
            return _USERS[value]
        raise ValidationError()

    def to_url(self, value):
        return _IDS[value]


def JsonApp(app):
    def error_handling(error):
        if isinstance(error, HTTPException):
            result = {
                "code": error.code,
                "description": error.description,
                "message": str(error),
            }
        else:
            description = abort.mapping[500].description
            result = {"code": 500, "description": description, "message": str(error)}
        resp = jsonify(result)
        resp.status_code = result["code"]
        return resp

    for code in default_exceptions:
        app.register_error_handler(code, error_handling)
    return app


class HTTPTimeoutAdapter(HTTPAdapter):
    def __init__(self, *args, **kw):
        self.timeout = kw.pop("timeout", 30.0)
        super().__init__(*args, **kw)

        def send(self, request, **kw):
            timeout = kw.get("timeout")
            if timeout is None:
                kw["timeout"] = self.timeout
            return super().send(request, **kw)


def setup_connector(app, name="default", **options):
    if not hasattr(app, "extensions"):
        app.extensions = {}
    if "connectors" not in app.extensions:
        app.extensions["connectors"] = {}
    session = Session()
    if "auth" in options:
        session.auth = options["auth"]
    headers = options.get("headers", {})
    if "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    session.headers.update(headers)

    retries = options.get("retries", 3)
    timeout = options.get("timeout", 30)
    adapter = HTTPTimeoutAdapter(max_retries=retries, timeout=timeout)
    session.mount("http://", adapter)

    app.extensions["connectors"][name] = session
    return session


def get_connector(app, name="default"):
    return app.extensions["connectors"][name]


app = JsonApp(Flask("microservice-flask"))
# app = Flask("microservice-flask")
setup_connector(app)

app.config.from_object(prod_settings.Config)
# app.config.from_object(Config)

app.url_map.converters["registered"] = RegisteredUser

app.register_blueprint(teams)


@app.route("/api", methods=["GET", "POST"])
def my_microservice():
    with get_connector(app) as conn:
        try:
            result = conn.get("http://localhost:5000/api", timeout=2.0).json()
        except (ReadTimeout, ConnectionError):
            result = {}
        return jsonify({"result": result, "Hello": "World!"})


@app.route("/api/person/<registered:name>")
def person(name):
    response = jsonify({"Hello hey": name})
    return response


@app.route("/api/job/<uuid:job_id>")
def job(job_id):
    return str(type(job_id))


@app.route("/api/path/<path:path>")
def path(path):
    print(f"path: {path}")
    return (str(type(path)), 200)


@app.route("/api/hello")
def hello():
    return jsonify({"Hello": g.user})


@app.route("/api/user/<user_id>", methods=["POST"])
def change_user(user_id):
    user = request.json
    # setting a new timestamp
    user["modified"] = _time2etag()
    _USERS[user_id] = user
    resp = jsonify(user)
    resp.set_etag(user["modified"])
    return resp


@app.route("/api/user/<user_id>")
def get_user(user_id):
    if user_id not in _USERS:
        return abort(404)
    user = _USERS[user_id]

    # returning 304 if If-None-Match matches
    if user["modified"] in request.if_none_match:
        return Response(status=304)

    resp = jsonify(user)

    # setting the ETag
    resp.set_etag(user["modified"])
    return resp


@app.before_request
def authenticate():
    if request.authorization:
        g.user = request.authorization["username"]
    else:
        g.user = "Anonymous"


def finished(sender, response, **extra):
    print(app)
    print("About to send a Response")
    print("sender:", sender)
    print("response:", response)


request_finished.connect(finished)


@app.errorhandler(500)
def error_handling(error):
    return jsonify({"Error": str(error)}, 500)


# @app.route("/api")
# def my_microservice():
#     return jsonify({"Hello": "World"})


if __name__ == "__main__":
    app.run()
