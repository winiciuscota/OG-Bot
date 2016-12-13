import unittest
import sys

from ogbot.scraping import general


class TestGeneral(unittest.TestCase):
    def test_parse_coordinates(self):
        self.assertEquals(general.parse_coordinates("[1:213:1]"), "1:213:1")
