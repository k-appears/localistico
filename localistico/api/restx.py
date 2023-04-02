import logging
import traceback

from flask_restx import Api
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

api = Api(version='1.0', title='TomTom integration API',
          description='Using Flask RestPlus with Swagger')


@api.errorhandler
def default_error_handler(exception):
    message = 'An unhandled exception occurred.'
    log.exception(exception)
    return {'message': message}, 500


# TODO create custom exception for integration with API
@api.errorhandler(ValueError)
def api_integration_error_handler(exception):
    log.warning(traceback.format_exc())
    return {'message': str(exception)}, 400


@api.errorhandler(NoResultFound)
def database_not_found_error_handler():
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404
