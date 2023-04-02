import os
import time
from unittest import TestCase

from localistico import step_2_3_4, settings
from localistico.database import db
from localistico.database.models import Status


class TestCompetitionInfo(TestCase):
    @classmethod
    def setUpClass(cls):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        db_dir = os.path.join(package_dir, 'test.db')
        sqlite_db = ''.join(['sqlite:///', db_dir])
        settings.SQLALCHEMY_DATABASE_URI = sqlite_db
        step_2_3_4.initialize_app(flask_app=step_2_3_4.app)
        step_2_3_4.app.config['TESTING'] = True
        step_2_3_4.app.config['DEBUG'] = False
        db.init_app(step_2_3_4.app)

    def setUp(self):
        with step_2_3_4.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with step_2_3_4.app.app_context():
            db.drop_all()

    def test_get(self):
        with step_2_3_4.app.test_client() as client:
            latitude = 51.51491
            longitude = -0.13331
            data = {'name': 'Pizzeria', 'latitude': latitude, 'longitude': longitude, 'country': 'GB'}
            response = client.get("/get_competition_info", query_string=data)

            self.assertDictEqual(response.json['business']['position'], {'lat': latitude, 'lon': longitude})

    def test_get_error_country(self):
        with step_2_3_4.app.test_client() as client:
            data = {'name': 'Pizzeria', 'latitude': 51.514934, 'longitude': -0.133228, 'country': 'ES'}
            response = client.get("/get_competition_info", query_string=data)
            self.assertTrue(response.status_code == 400)
            self.assertEqual(response.json["message"], '{\'country\': [\'Must be one of: GB.\']}')

    def test_get_error_max_length(self):
        with step_2_3_4.app.test_client() as client:
            latitude = 51.51491
            longitude = -0.13331
            data = {'name': 'Pizzeriaaaaaaaaaaaaaaaaaaa', 'latitude': latitude, 'longitude': longitude, 'country': 'GB'}
            response = client.get("/get_competition_info", query_string=data)

            self.assertEqual(response.json["message"], "{'name': ['Length must be between 1 and 20.']}")

    def test_get_error_no_name(self):
        with step_2_3_4.app.test_client() as client:
            latitude = 51.51491
            longitude = -0.13331
            data = {'latitude': latitude, 'longitude': longitude, 'country': 'GB'}
            response = client.get("/get_competition_info", query_string=data)

            self.assertEqual(response.json["message"], "{'name': ['Missing data for required field.']}")

    def test_get_error_no_latitude(self):
        with step_2_3_4.app.test_client() as client:
            longitude = -0.13331
            data = {'name': 'Pizzeria', 'longitude': longitude, 'country': 'GB'}
            response = client.get("/get_competition_info", query_string=data)

            self.assertEqual(response.json["message"], "{'latitude': ['Missing data for required field.']}")

    def test_get_async(self):
        with step_2_3_4.app.test_client() as client:
            latitude = 51.51491
            longitude = -0.13331
            data = {'name': 'Pizzeria', 'latitude': latitude, 'longitude': longitude, 'country': 'GB'}
            response_async = client.get("/get_competition_info_async", query_string=data)

            response = client.get(f'/task/{int(response_async.data)}')

            self.assertEqual(response.json['status'], Status.submitted.name)

    def test_get_async_task(self):
        with step_2_3_4.app.test_client() as client:
            latitude = 51.51491
            longitude = -0.13331
            data = {'name': 'Pizzeria', 'latitude': latitude, 'longitude': longitude, 'country': 'GB'}
            response_async = client.get("/get_competition_info_async", query_string=data)

            time.sleep(2)  # Wait to make the call to external API
            place_id, retry = None, 0
            while not place_id and retry < 10:
                response = client.get(f'/task/{int(response_async.data)}')
                place_id = response.json['place_id']
                retry = retry + 1
                time.sleep(1)

            self.assertEqual(response.json['status'], Status.completed.name)
