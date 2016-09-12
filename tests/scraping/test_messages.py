import unittest
import sys
import datetime

sys.path.append('../..')

from ogbot.scraping import messages


class MessagesTest(unittest.TestCase):
    def test_parse_resource(self):
        self.assertEquals(messages.parse_resource("Metal: 2.492M"), 2492000)
        self.assertEquals(messages.parse_resource("Metall: 1,089M"), 1089000)
        self.assertEquals(messages.parse_resource("Deuterium: 75.000"), 75000)
        self.assertEquals(messages.parse_resource("Defesas: 0"), 0)
        self.assertEquals(messages.parse_resource(" Defesas: 771.000"), 771000)

    def test_parse_loot_percentage(self):
        self.assertEquals(messages.parse_loot_percentage(" Loot: 50%"), .5)
        self.assertEquals(messages.parse_loot_percentage(" Roubo: 75%"), .75)
        self.assertEquals(messages.parse_loot_percentage("Loot:  50%"), .5)

    def test_parse_report_datetime(self):
        self.assertEquals(messages.parse_report_datetime("03.04.2016 00:25:13"),
                          datetime.datetime(2016, 4, 3, 0, 25, 13))
        self.assertEquals(messages.parse_report_datetime("02.04.2016 23:38:23"),
                          datetime.datetime(2016, 4, 2, 23, 38, 23))
        self.assertEquals(messages.parse_report_datetime("02.04.2016 23:38:20"),
                          datetime.datetime(2016, 4, 2, 23, 38, 20))
