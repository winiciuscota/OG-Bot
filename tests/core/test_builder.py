import unittest
from mock import Mock

from ogbot.core import builder
from ogbot.scraping import buildings


class TestBuilder(unittest.TestCase):
    def setup_test_filter_available_buildings(self):
        self.config_mock1 = Mock(build_solar_plant=True, build_fusion_reactor=True, build_storage=True)
        self.config_mock2 = Mock(build_solar_plant=False, build_fusion_reactor=True, build_storage=False)
        self.config_mock3 = Mock(build_solar_plant=False, build_fusion_reactor=False, build_storage=False)

        self.available_buildings_stub = []
        self.available_buildings_stub.append(buildings.BUILDINGS_DATA.get('sp'))
        self.available_buildings_stub.append(buildings.BUILDINGS_DATA.get('fr'))
        self.available_buildings_stub.append(buildings.BUILDINGS_DATA.get('cs'))
        self.available_buildings_stub.append(buildings.BUILDINGS_DATA.get('ms'))
        self.available_buildings_stub.append(buildings.BUILDINGS_DATA.get('dt'))

    def test_filter_available_buildings(self):
        self.setup_test_filter_available_buildings()

        self.assertEquals(5, len(builder.BuilderBot.filter_available_buildings(self.available_buildings_stub,
                                                                               self.config_mock1)))
        self.assertEquals(1, len(builder.BuilderBot.filter_available_buildings(self.available_buildings_stub,
                                                                               self.config_mock2)))
        self.assertEquals(0, len(builder.BuilderBot.filter_available_buildings(self.available_buildings_stub,
                                                                               self.config_mock3)))
