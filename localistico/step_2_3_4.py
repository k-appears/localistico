"""
The API will consist of one single method that will be accessible by a GET request to the
    endpoint /get_competition_info
● The endpoint should wrap the method implemented in Step 1
         ○ it should accept the same parameters
         ○ it should return the same result in JSON format
● Validate all the inputs, if the validation fails, return an error:
         ○ name parameter should not be longer than 20 characters
         ○ this endpoint should only support UK, any other country should return an error
         ○ think about what other validations could you add here
● Write some tests for the API.



    Why flask?
    ==========

    Because for an MVP, Flask provides finer granular modularization than Django
"""

import logging.config
from pathlib import Path

from flask import Flask, Blueprint

from localistico import settings
from localistico.api.resource.business import ns as place_namespace
from localistico.api.restx import api
from localistico.database import db

app = Flask(__name__)
logging.config.fileConfig(Path(__file__).parent / './resources' / 'logging.conf')
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['FLASK_ENV'] = settings.FLASK_ENV
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/')
    api.init_app(blueprint)
    api.add_namespace(place_namespace)
    flask_app.register_blueprint(blueprint)


def initialize_db():
    db.init_app(app)
    with app.app_context():
        db.create_all()


def main():
    initialize_app(app)
    initialize_db()
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
