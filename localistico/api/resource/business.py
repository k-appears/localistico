"""Logic of handling requests to obtain competitors from a business"""
import logging
from concurrent.futures import ThreadPoolExecutor

from flask import request, abort
from flask_restx import Resource
from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from localistico import step_1, settings
from localistico.api.restx import api
from localistico.database.models import Task, Status

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
executor = ThreadPoolExecutor(2)

log = logging.getLogger(__name__)

ns = api.namespace('', description='Integration with TomTom to get competitors of a POI')


class PlaceQuerySchema(Schema):
    """Validations are done using marshmallow instead of argparse because argparse is deprecated"""
    name = fields.Str(required=True, validate=Length(1, 20))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    country = fields.Str(validate=OneOf(['GB']))


@ns.route('/get_competition_info', doc={'description': 'Find the 10 closest competing businesses'})
@api.response(400, 'Validation error')
class Business(Resource):
    @api.doc(params={'name': {'description': 'business name to obtain competitors, max length 20',
                              'max_length': 20, 'example': 'Pizza', 'required': True}})
    @api.doc(params={'latitude': {'required': True}})
    @api.doc(params={'longitude': {'required': True}})
    @api.doc(params={'country': {'description': 'Only country supported is GB', 'enum': ['GB'], 'required': True}})
    @api.response(200, 'Success')
    def get(self):
        errors = PlaceQuerySchema().validate(request.args)
        if errors:
            abort(400, str(errors))

        name = request.args.get('name')
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        return step_1.competition_info(name=name, location=step_1.Location(latitude=latitude, longitude=longitude),
                                       countrySet='GB')


@ns.route('/get_competition_info_async',
          doc={'description': 'Request to calculate the 10 closest competing businesses'})
class AsyncBusiness(Resource):
    """
    Step 3: Run It in the Background
    In this step the API becomes asynchronous. The flow of the API will change slightly:
        ● Add a new endpoint, /get_competition_info_async, that will do the same thing as
             the endpoint implemented in Step 2, but in a background task.
        ● Each background task gets assigned an ID
        ● There should be an endpoint for the client to get the result of any previous task for which they know the ID.
        ● If there’s a failure during execution, the task should retry up to 3 times.
        ● If all 3 attempts fail, the task should be marked as failed.
        ● Write some tests for this endpoint.
    """

    @api.doc(params={'name': {'description': 'business name to obtain competitors, max length 20',
                              'max_length': 20, 'example': 'Pizza', 'required': True}})
    @api.doc(params={'latitude': {'required': True}})
    @api.doc(params={'longitude': {'required': True}})
    @api.doc(params={'country': {'description': 'Only country supported is GB', 'enum': ['GB'], 'required': True}})
    @api.response(200, 'Success')
    def get(self):
        errors = PlaceQuerySchema().validate(request.args)
        if errors:
            abort(400, str(errors))
        name = request.args.get('name')
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        task = Task()
        task.status = Status.submitted
        task.save()

        executor.submit(self.request_competition_info, name, latitude, longitude, task.id)

        return task.id, 201

    @staticmethod
    def request_competition_info(name, latitude, longitude, task_id):
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        session_maker = sessionmaker(bind=engine)
        session = session_maker()
        task = session.query(Task).filter(Task.id == task_id).one()
        tries, success, error, result = 1, False, None, None
        while tries < 4 and not success:
            try:
                result = step_1.competition_info(name=name, location=step_1.Location(
                    latitude=latitude, longitude=longitude), countrySet='GB')
                success = True
            except ValueError as err:
                error = str(err)
                logging.error(f'retrying task with id={task.id}, err: {error} ')
                tries = tries + 1

        if tries == 4:
            task.status = Status.aborted
            task.error_message = error
            session.add(task)
            session.commit()
            session.close()
            engine.dispose()
            return

        # TODO place can be persisted without traversing results
        task.place_id = result['business']['id']
        task.name = result['business']['name']
        task.lat = result['business']['position']['lat']
        task.lon = result['business']['position']['lon']
        task.address = result['business']['address']
        task.phone = result['business']['phone_number']

        task.rating_comparison = result['rating_comparison']

        task.circle_lat = result['visualisation_circle'][0]
        task.circle_lon = result['visualisation_circle'][1]
        task.circle_radius = result['visualisation_circle'][2]

        task.status = Status.completed
        session.add(task)
        session.commit()
        session.close()
        engine.dispose()


@ns.route('/task/<int:task_id>', doc={'description': 'Get business requested previously'})
class GetBusiness(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Business not found.')
    def get(self, task_id):
        return Task.query.filter(Task.id == task_id).one().serialized()
