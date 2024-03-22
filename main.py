from typing import Type

import flask
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from models import Posted, Session
from schema import CreatePosted, UpdatePosted

app = Flask('app')


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response: flask.Response):
    request.session.close()
    return response


def valid_json(json_data: dict, schema_class: Type[CreatePosted] | Type[UpdatePosted]):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop('ctx', None)
        raise HttpError(status_code=400, message=error)


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response


def get_posted(posted_id: int):
    posted = request.session.query(Posted).get(posted_id)
    if posted is None:
        raise HttpError(status_code=404, message='not found')
    else:
        return posted


def create_posted(posted: Posted):
    try:
        request.session.add(posted)
        request.session.commit()
    except IntegrityError:
        raise HttpError(status_code=409, message='user already exist')


class PostedView(MethodView):

    def post(self):
        data_post = valid_json(request.json, CreatePosted)
        posted = Posted(**data_post)
        create_posted(posted)
        return jsonify(posted.dict)

    def get(self, posted_id: int):
        posted = get_posted(posted_id)
        return jsonify(posted.dict)

    def patch(self, posted_id: int):
        data_post = request.json
        posted = get_posted(posted_id)
        for field, value in data_post.items():
            setattr(posted, field, value)
        create_posted(posted)
        return jsonify(posted.dict)

    def delete(self, posted_id: int):
        posted = get_posted(posted_id)
        request.session.delete(posted)
        request.session.commit()
        return jsonify({'status': 'delete'})


posted_view = PostedView.as_view('posted_view')


app.add_url_rule(rule='/posted/', view_func=posted_view, methods=['POST'])

app.add_url_rule(rule='/posted/<int:posted_id>', view_func=posted_view, methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    app.run(debug=True)