from unittest import TestCase
from unittest.mock import patch, Mock

from localistico.step_1 import competition_info, Location


class Test(TestCase):
    first_return = {"poiCategories": [{'name': 'Pizza'}]}
    item = {'score': 1,
            'position': {'lat': 1, 'lon': -1},
            'id': 'id_1',
            'address': {'freeformAddress': 'Address 1'},
            'poi': {'phone': '+34 0000000', 'name': 'Name 1'}}
    second_return = {'results': [item]}

    @patch('requests.get')  # Mock 'requests' module 'get' method.
    @patch('jsonschema.validate')
    def test_competition_info_call_invalid_cat(self, mock_validate, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = {"poiCategories": [{'name': 'Pizzeria'}]}
        mock_validate.return_value = None
        with self.assertRaises(ValueError) as context:
            competition_info("pizza", Location(1.0, -1.0))

        self.assertTrue("pizza not in TomTom available categories" in str(context.exception))

    @patch('requests.get')  # Mock 'requests' module 'get' method.
    @patch('jsonschema.validate')
    def test_competition_info_request(self, mock_validate, mock_get):
        mock_get.return_value = Mock(status_code=200)

        mock_get.return_value.json.side_effect = [self.first_return, self.second_return, self.second_return]
        mock_validate.return_value = None

        competition_info("Pizza", Location(1.0, -1.0))

        get_call_poi = mock_get.call_args_list
        self.assertGreaterEqual(get_call_poi[1].kwargs['params'].items(), {'limit': 1, 'lat': 1.0, 'lon': -1.0}.items())
        self.assertGreaterEqual(get_call_poi[2].kwargs['params'].items(),
                                {'limit': 11, 'lat': 1.0, 'lon': -1.0}.items())

    @patch('requests.get')
    @patch('jsonschema.validate')
    @patch('flask_sqlalchemy_swagger.utils.smallestenclosingcircle.make_circle')
    def test_competition_circle_zero_competitors(self, mock_make_circle, mock_validate, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.side_effect = [self.first_return, self.second_return, self.second_return]
        mock_validate.return_value = None

        competition_info("Pizza", Location(1.0, -1.0))

        mock_make_circle.assert_called_with([])

    @patch('requests.get')
    @patch('jsonschema.validate')
    @patch('flask_sqlalchemy_swagger.utils.smallestenclosingcircle.make_circle')
    def test_competition_score(self, mock_make_circle, mock_validate, mock_get):
        mock_make_circle.return_value = 1, 2, 3
        mock_get.return_value = Mock(status_code=200)
        third_return = {'results': [dict(self.item, **{'score': 3, 'position': {'lat': 2, 'lon': 2}})]}
        mock_get.return_value.json.side_effect = [self.first_return, self.second_return, third_return]
        mock_validate.return_value = None

        result = competition_info("Pizza", Location(1.0, -1.0))

        self.assertEqual(result['rating_comparison'], -2.0)

    @patch('requests.get')
    @patch('jsonschema.validate')
    @patch('flask_sqlalchemy_swagger.utils.smallestenclosingcircle.make_circle')
    def test_competition_score_zero_competitors(self, mock_make_circle, mock_validate, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.side_effect = [self.first_return, self.second_return, self.second_return]
        mock_validate.return_value = None

        result = competition_info("Pizza", Location(1.0, -1.0))

        self.assertEqual(result['business']['score'], 1)

    @patch('requests.get')  # Mock 'requests' module 'get' method.
    @patch('jsonschema.validate')
    def test_competition_info_not_found_place(self, mock_validate, mock_get):
        mock_get.return_value = Mock(status_code=200)
        first_return = {"poiCategories": [{'name': 'Pizza'}]}
        second_return = {'properties': {'results': {'items': []}}}
        mock_get.return_value.json.side_effect = [first_return, second_return]
        mock_validate.return_value = None

        with self.assertRaises(ValueError) as context:
            competition_info("pizza", Location(1.0, -1.0))

            self.assertTrue("Place not found with category Pizza and coordinates lat: 1.0, lon: -1.0"
                            in str(context.exception))
