from flask import Flask, jsonify, request
from werkzeug.routing import BaseConverter, ValidationError

_USERS = {'1': 'Tarek', '2': 'Freya'}

_IDS = {val: id for id, val in _USERS.items()}

class RegisteredUser(BaseConverter):
    def to_python(self, value):
        if value in _USERS:
            return _USERS[value]
        raise ValidationError()
    def to_url(self, value):
        return _IDS[value]

app = Flask(__name__)

app.url_map.converters['registered'] = RegisteredUser

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

if __name__ == '__main__':
    app.run()