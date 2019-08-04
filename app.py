from flask import Flask, jsonify, g, request, request_finished, abort
from requests import Session
from requests.exceptions import ReadTimeout, ConnectionError
from requests.adapters import HTTPAdapter
from werkzeug.exceptions import HTTPException, default_exceptions
from werkzeug.routing import BaseConverter, ValidationError

from flask.signals import signals_available

from teams import teams


if not signals_available:
    raise RuntimeError("pip install blinker")


_USERS = {'1': 'Tarek', '2': 'Freya'}

_IDS = {val: id for id, val in _USERS.items()}


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
            result = {'code': error.code, 'description': error.description, 'message': str(error)}
        else:
            description = abort.mapping[500].description
            result = {'code': 500, 'description': description, 'message': str(error)}
        resp = jsonify(result)
        resp.status_code = result['code']
        return resp

    for code in default_exceptions:
        app.register_error_handler(code, error_handling)
    return app


class HTTPTimeoutAdapter(HTTPAdapter):
    def __init__(self, *args, **kw):
        self.timeout = kw.pop('timeout', 30.)
        super().__init__(*args, **kw)

        def send(self, request, **kw):
            timeout = kw.get('timeout')
            if timeout is None:
                kw['timeout'] = self.timeout
            return super().send(request, **kw)


def setup_connector(app, name='default', **options):
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    if 'connectors' not in app.extensions:
        app.extensions['connectors'] = {}
    session = Session()
    if 'auth' in options:
        session.auth = options['auth']
    headers = options.get('headers', {})
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    session.headers.update(headers)

    retries = options.get('retries', 3)
    timeout = options.get('timeout', 30)
    adapter = HTTPTimeoutAdapter(max_retries=retries, timeout=timeout)
    session.mount('http://', adapter)

    app.extensions['connectors'][name] = session
    return session


def get_connector(app, name='default'):
    return app.extensions['connectors'][name]


app = JsonApp(Flask("microservice-flask"))
# app = Flask("microservice-flask")
setup_connector(app)

app.config.from_object('config.prod_settings.Config')

app.url_map.converters['registered'] = RegisteredUser

app.register_blueprint(teams)


@app.route('/api', methods=['GET', 'POST'])
def my_microservice():
    with get_connector(app) as conn:
        try:
            result = conn.get('http://localhost:5000/api', timeout=2.0).json()
        except (ReadTimeout, ConnectionError):
            result = {}
        return jsonify({'result': result, 'Hello': 'World!'})


@app.route('/api/person/<registered:name>')
def person(name):
    response = jsonify({'Hello hey': name})
    return response


@app.route('/api/job/<uuid:job_id>')
def job(job_id):
    return str(type(job_id))


@app.route('/api/path/<path:path>')
def path(path):
    print(f"path: {path}")
    return (str(type(path)), 200)


@app.route('/api/hello')
def hello():
    return jsonify({'Hello': g.user})


@app.before_request
def authenticate():
    if request.authorization:
        g.user = request.authorization['username']
    else:
        g.user = 'Anonymous'


def finished(sender, response, **extra):
    print(app)
    print('About to send a Response')
    print('sender:', sender)
    print('response:', response)


request_finished.connect(finished)


@app.errorhandler(500)
def error_handling(error):
    return jsonify({'Error': str(error)}, 500)


@app.route('/api')
def my_microservice():
    return jsonify({"Hello": "World"})


if __name__ == '__main__':
    app.run()