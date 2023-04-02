from unittest import TestCase

from localistico.step_1 import competition_info, Location


class TestStep1(TestCase):
    def test_competition_info(self):
        lat, lon = 37.340179, -5.929498
        result = competition_info("Pizzeria", Location(latitude=lat, longitude=lon))
        self.assertDictEqual(result,
                             {'business': {'score': 2.5745279789, 'position': {'lat': 37.34015, 'lon': -5.92943},
                                           'id': 'g6JpZK83MjQwMDkwMzA3ODQ0NzKhY6NFU1ChdqdVbmlmaWVk',
                                           'address': 'Calle de Venecia 0012, 41089 Dos Hermanas',
                                           'phone_number': '', 'name': 'Pizzeria Erma'}, 'visualisation_circle': (
                                 37.354045731005804, -5.9533625417947444, 0.027935194103162406),
                              'rating_comparison': 0.0033620834400003297})
