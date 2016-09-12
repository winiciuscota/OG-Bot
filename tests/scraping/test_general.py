import unittest
import sys
import datetime

sys.path.append('../..')

from ogbot.scraping import general


class GeneralTest(unittest.TestCase):
    def test_parse_coordinates(self):
        self.assertEquals(general.parse_coordinates("[1:213:1]"), "1:213:1")
