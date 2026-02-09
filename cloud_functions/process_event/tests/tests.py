import json
import os
import time
import unittest

from processors.categories import categorize
from processors.genres import assign_genres
from processors.themes import assign_themes
from processors.venues import connect_to_venue


def process_event(event: dict) -> dict:
    event = categorize(event)
    if event["category_include"]:
        event = connect_to_venue(event)
        event = assign_themes(event)
        if event["category_name"] == "Concert" or event["category_name"] == "Club":
            event = assign_genres(event)
    return event


@unittest.skip
class TestNortic(unittest.TestCase):

    def test_t_centralen(self):
        with open("source_nortic/T-CENTRALEN.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            self.assertIsNone(obj=event.get("venue_id"))


@unittest.skip
class TestSvenskakyrkan(unittest.TestCase):

    def test_venue(self):
        with open("source_svenskakyrkan/LLO  Leenas Lilla Orkester.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            self.assertIsNone(obj=event.get("venue_id"))


@unittest.skip
class TestTicketmaster(unittest.TestCase):

    def test_venue(self):
        with open(
            "source_ticketmaster/Måns Möller - Mitt perfekta liv.json", "r"
        ) as file:
            event = json.load(file)
            event = process_event(event)
            self.assertIsNone(obj=event.get("venue_id"))


@unittest.skip
class TestOneThemeAngGenre(unittest.TestCase):

    def test_single_theme_id(self):
        test_files_dir = "one_theme_and_genre"
        for file_name in os.listdir(test_files_dir):
            with open(f"{test_files_dir}/{file_name}", "r") as file:
                event = json.load(file)
                event = process_event(event)
                if event.get("theme_ids"):
                    self.assertLessEqual(
                        a=len(event.get("theme_ids")),
                        b=1,
                        msg=f"{file_name} - {event.get('theme_ids')}",
                    )
                if event.get("genre_ids"):
                    self.assertLessEqual(
                        a=len(event.get("genre_ids")),
                        b=1,
                        msg=f"{file_name} - {event.get('genre_ids')}",
                    )


@unittest.skip
class TestNarrowTheme(unittest.TestCase):

    def setUp(self):
        print("Sleep before running test")
        time.sleep(3)  # sleep time in seconds

    def test_event_id_1962(self):
        with open("narrow_theme/Vindlaboratoriet (2-4 år).json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=2, second=next(iter(theme_ids), None))

    def test_event_id_5475(self):
        with open("narrow_theme/Ebbot Lundberg & The Solar Circus.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_13080(self):
        with open("narrow_theme/BIRDS (COME BACK TO BONES).json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=5, second=next(iter(theme_ids), None))

    def test_event_id_13704(self):
        with open(
            "narrow_theme/Gustaf & Viktor Noréns jul Cassels (Matiné).json", "r"
        ) as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=3, second=next(iter(theme_ids), None))

    def test_event_id_14370(self):
        with open("narrow_theme/Begynnelsen.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=1, second=next(iter(theme_ids), None))

    def test_event_id_14577(self):
        with open("narrow_theme/Nötknäpparen.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=3, second=next(iter(theme_ids), None))

    def test_event_id_16166(self):
        with open("narrow_theme/Steamy Christmas.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=3, second=next(iter(theme_ids), None))

    def test_event_id_21332(self):
        with open("narrow_theme/Julkonsert.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=3, second=next(iter(theme_ids), None))

    def test_event_id_22043(self):
        with open("narrow_theme/Bamse och Sjörövarskatten.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=2, second=next(iter(theme_ids), None))

    def test_event_id_27708(self):
        with open("narrow_theme/Patrik Larsson & Viktor Wu.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=1, second=next(iter(theme_ids), None))

    def test_event_id_27921(self):
        with open("narrow_theme/VINTERPJÄSEN.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_28893(self):
        with open("narrow_theme/Wreck of Blues Flying Circus LÖRDAG.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_29156(self):
        with open(
            "narrow_theme/Måns Möller – Mitt perfekta liv 2025 (19.00).json", "r"
        ) as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=1, second=next(iter(theme_ids), None))

    def test_event_id_36825(self):
        with open(
            "narrow_theme/Familjekonsert Barnvisor av och med Jojje Wadenius.json", "r"
        ) as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=2, second=next(iter(theme_ids), None))

    def test_event_id_41439(self):
        with open("narrow_theme/P3 Guld.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_43075(self):
        with open("narrow_theme/Snögubben.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=2, second=next(iter(theme_ids), None))

    def test_event_id_43229(self):
        with open("narrow_theme/Girls Night Out på Barbros.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_43232(self):
        with open(
            "narrow_theme/A Yah Soh Nice - Vol 1 Dancers Edition.json", "r"
        ) as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_43326(self):
        with open("narrow_theme/Flashdance - The Musical.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_43725(self):
        with open("narrow_theme/Elvis 90 år - Burträskarnas hus.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)

    def test_event_id_44334(self):
        with open("narrow_theme/Omätbara.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=5, second=next(iter(theme_ids), None))

    def test_event_id_45487(self):
        with open(
            "narrow_theme/VIVA SOUNDS Majvi Superstar + We are wood.json", "r"
        ) as file:
            event = json.load(file)
            event = process_event(event)
            theme_ids = event.get("theme_ids")
            self.assertEqual(first=[], second=theme_ids)


@unittest.skip
class TestCategoriesWithDefinition(unittest.TestCase):
    def test_event_id_74084(self):
        with open("categories_with_definitions/74084.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=9, second=category_id)

    def test_event_id_38723(self):
        with open("categories_with_definitions/38723.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=9, second=category_id)

    def test_event_id_45604(self):
        with open("categories_with_definitions/45604.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=9, second=category_id)

    def test_event_id_68270(self):
        with open("categories_with_definitions/68270.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=10, second=category_id)

    def test_event_id_55580(self):
        with open("categories_with_definitions/55580.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=10, second=category_id)

    def test_event_id_7916(self):
        with open("categories_with_definitions/7916.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=10, second=category_id)

    def test_event_id_39167(self):
        with open("categories_with_definitions/39168.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=10, second=category_id)

    def test_event_id_57720(self):
        with open("categories_with_definitions/57720.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=18, second=category_id)

    def test_event_id_70955(self):
        with open("categories_with_definitions/70955.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=18, second=category_id)

    def test_event_id_40001(self):
        with open("categories_with_definitions/40001.json", "r") as file:
            event = json.load(file)
            event = process_event(event)
            category_id = event.get("category_id")
            self.assertEqual(first=30, second=category_id)


if __name__ == "__main__":
    unittest.main()
