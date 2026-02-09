from unittest import TestCase

from cloud_functions.push_to_bubble.main import to_venue_hint


class Test(TestCase):
    def test_to_venue_hint_all_fields_exist_correct_output(self):
        venue = {
            "city": "New York",
            "address_text": "123 Main St",
            "zipcode": 10001,
            "name": "Empire State Building",
            "coordinates": {
                "latitude": 40.748817,
                "longitude": -73.985428,
            },  # Dictionary format
        }
        self.assertEqual(
            to_venue_hint(venue),
            "Empire State Building, 123 Main St, 10001 New York, (40.748817, -73.985428)",
        )

    def test_to_venue_hint_missing_coordinates_correct_output(self):
        venue = {
            "city": "New York",
            "address_text": "123 Main St",
            "zipcode": 10001,
            "name": "Empire State Building",
        }
        self.assertEqual(
            to_venue_hint(venue), "Empire State Building, 123 Main St, 10001 New York"
        )

    def test_to_venue_hint_missing_city_correct_output(self):
        venue = {
            "address_text": "123 Main St",
            "zipcode": 10001,
            "name": "Empire State Building",
            "coordinates": {
                "latitude": 40.748817,
                "longitude": -73.985428,
            },  # Dictionary format
        }
        self.assertEqual(
            to_venue_hint(venue),
            "Empire State Building, 123 Main St, 10001, (40.748817, -73.985428)",
        )

    def test_to_venue_hint_missing_address_correct_output(self):
        venue = {
            "city": "New York",
            "zipcode": 10001,
            "name": "Empire State Building",
            "coordinates": {
                "latitude": 40.748817,
                "longitude": -73.985428,
            },  # Dictionary format
        }
        self.assertEqual(
            to_venue_hint(venue),
            "Empire State Building, 10001 New York, (40.748817, -73.985428)",
        )

    def test_to_venue_hint_missing_zipcode_correct_output(self):
        venue = {
            "city": "New York",
            "address_text": "123 Main St",
            "name": "Empire State Building",
            "coordinates": {
                "latitude": 40.748817,
                "longitude": -73.985428,
            },  # Dictionary format
        }
        self.assertEqual(
            to_venue_hint(venue),
            "Empire State Building, 123 Main St, New York, (40.748817, -73.985428)",
        )
