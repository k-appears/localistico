#
# ● Create a function or a method that accepts the following parameters
#          ○ a string containing the name of a business
#          ○ a location object with 2 attributes, latitude and longitude
# ● Get competition info for a business (one place) described by these parameters with the
#     help of the TomTom Search API .
#          ○ identify the business the user wanted to find among the returned results
#          ○ find 10 closest competing businesses ( competition )
#                    ■ competing means same category/categories
#          ○ calculate rating comparison : how much better or worse is the business compared
#               to the total average of its competition (business rating - competition avg.rating)
#          ○ calculate visualisation circle: to show the info on the map, calculate a circle that
#               covers the business and all its competition
# ● The result must contain the following:
#          ○ the business: id, name, address, coordinates and phone number
#          ○ visualisation circle
#          ○ rating comparison
# ● Write some tests for this method.
import json
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from pathlib import Path

import jsonschema
import requests

# TODO in config file for a server
from localistico.utils import smallestenclosingcircle

END_POINT = "https://api.tomtom.com/search/2"
KEY = "nt0WpoWFNPf7PxPWE2qcHgjtthK73CPY"
REFERER = 'https://developer.tomtom.com/content/search-api-explorer'
# curl -X GET "https://api.tomtom.com/search/2/poiCategories.json?key=nt0WpoWFNPf7PxPWE2qcHgjtthK73CPY" -H 'Referer: https://developer.tomtom.com/content/search-api-explorer' > categories.json
cat_schema_path = Path(__file__).parent / './resources' / 'categories_schema.json'
poi_schema_path = Path(__file__).parent / './resources' / 'poi_schema.json'


def load_json(path_file: Path):
    with path_file.open() as json_file:
        return json.load(json_file)


@dataclass
class Location:
    latitude: float
    longitude: float


def competition_info(name: str, location: Location, **optional_params):
    """
    find 10 closest competing businesses ( competition )


    Exercise assumptions:
    + 'name' parameter refers to TomTom Category
    https://developer.tomtom.com/search-api/search-api-documentation-search/category-search
    + rating: Described in https://developer.tomtom.com/search-api/search-api-documentation/points-of-interest-details
    + circle: Requires to find smallest circle of points several https://en.wikipedia.org/wiki/Smallest-circle_problemm


     Technical assumptions:
     + TomTom API requires a Key, the key used in https://developer.tomtom.com/content/search-api-explorer I assume it
     won't change, when click on "Try out" the query parameter key of requests are nt0WpoWFNPf7PxPWE2qcHgjtthK73CPY
     + Categories are listed in
     https://developer.tomtom.com/content/search-api-explorer#/POI%20Categories/get_search__versionNumber__poiCategories__ext_
     if input category not in listed, an error is raised
     + Rating: Requires a call to
     https://developer.tomtom.com/search-api/search-api-documentation-search/points-interest-search
     to extract the ID of the business
     + Circle: Use API https://www.nayuki.io/res/smallest-enclosing-circle/smallestenclosingcircle.py

    :param name: TomTom business category
    :param location: With longitude and latitude
    :return: business: Information with id, name, address, coordinates and phone_number
          visualisation_circle: With longitude, latitude and radius
          rating_comparison: Number to compare with 10 competition
    """

    # curl -X GET "https://api.tomtom.com/search/2/poiCategories.json?key=nt0WpoWFNPf7PxPWE2qcHgjtthK73CPY" \
    # -H 'Referer: https://developer.tomtom.com/content/search-api-explorer'
    url_categories = f'{END_POINT}/poiCategories.json'
    json_cat = get_request_tomtom(url_categories)
    validate_json(json_cat, cat_schema_path)
    if name not in (category['name'] for category in json_cat["poiCategories"]):
        raise ValueError(f'Input parameter name {name} not in TomTom available categories. '
                         'See https://developer.tomtom.com/content/search-api-explorer#/POI%20Categories/')

    places = get_points_of_interest(location, name, limit=1, **optional_params)
    if len(places) != 1:
        raise ValueError(f'Place not found with category {name} and coordinates lat: {location.latitude}, '
                         f'lon: {location.longitude} and {optional_params}')
    place: dict = places[0]
    competition = list(
        filter(lambda x: x['position'] != place['position'], get_points_of_interest(location, name, limit=11)))
    rating = calculate_rating(competition, place)

    points = [(float(c_place['position']['lat']), float(c_place['position']['lon'])) for c_place in competition]
    circle = smallestenclosingcircle.make_circle(points)

    return {'business': place, 'visualisation_circle': circle, 'rating_comparison': rating}


def calculate_rating(competition, place):
    if len(competition) == 0:
        return place['score']
    avg = sum(c_place['score'] for c_place in competition) / len(competition)
    rating = place['score'] - avg
    return rating


def get_points_of_interest(location, name, limit, **optional_params):
    # curl 'https://api.tomtom.com/search/2/categorySearch/Pizzeria.json?lat=37.340179&lon=-5.929498&key=nt0WpoWFNPf7PxPWE2qcHgjtthK73CPY&limit=10'  -H 'Referer: https://developer.tomtom.com/content/search-api-explorer'
    url_pois = f'{END_POINT}/categorySearch/{name}.json'
    parameters = {'limit': limit, 'lat': location.latitude, 'lon': location.longitude}
    parameters.update(optional_params)
    json_pois = get_request_tomtom(url_pois, parameters=parameters)
    validate_json(json_pois, poi_schema_path)
    return [{'score': item['score'],
             'position': item['position'],
             'id': item['id'],
             'address': item['address']['freeformAddress'],
             'phone_number': item['poi']['phone'] if 'phone' in item['poi'] else '',
             'name': item['poi']['name']}
            for item in json_pois['results']]


def get_request_tomtom(url: str, parameters=None):
    try:
        # TODO Not used retries
        # TODO Not Throttling implemented
        params = parameters if parameters else {}
        params.update({'key': KEY})
        resp = requests.get(url=url, params=params, headers={'referer': REFERER})
        resp.raise_for_status()
        json_data = resp.json()
    except requests.exceptions.HTTPError as err:
        raise ValueError(err) from requests.exceptions.HTTPError
    except JSONDecodeError:
        # TODO To test it, spy to change url or pass it as parameter
        raise ValueError(f'Request to {url}, Response does not contain a valid JSON') from JSONDecodeError
    return json_data


def validate_json(json_data, path_schema: Path):
    try:
        schema = load_json(path_schema)
        jsonschema.validate(instance=json_data, schema=schema)
    except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError) as err:
        # TODO Do not forget when creating web server
        raise ValueError(f'Error validating json obtained with a schema {path_schema}') from err


if __name__ == "__main__":
    lat, lon = 37.340179, -5.929498
    competition_info("Pizzeria", Location(latitude=lat, longitude=lon))
