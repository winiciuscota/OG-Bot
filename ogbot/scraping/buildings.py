from bs4 import BeautifulSoup
import re
from general import General
from scraper import *


class BuildingTypes(Enum):
    """
    1. Mina de metal
    2. Mina de critstal
    3. Sintetizador de delterio
    4. Planta de energia solar
    5. Planta de fusao
    ...
    """
    MetalMine = "1"
    CrystalMine = "2"
    DeuteriumSynthesizer = "3"
    SolarPlant = "4"
    FusionReactor = "12"
    SolarSatellite = "202"
    MetalStorage = "22"
    CrystalStorage = "23"
    DeuteriumTank = "24"


BUILDINGS_DATA = {

    "mm": BuildingItem(1, "Metal Mine"),
    "cm": BuildingItem(2, "Crystal Mine"),
    "ds": BuildingItem(3, "Deuterium Synthesizer"),
    "sp": BuildingItem(4, "Solar Plant"),
    "fr": BuildingItem(12, "Fusion Reactor"),
    "ms": BuildingItem(22, "Metal Storage"),
    "cm": BuildingItem(23, "Crystal Storage"),
    "dt": BuildingItem(24, "Deuterium Tank"),

    "1": BuildingItem(1, "Metal Mine"),
    "2": BuildingItem(2, "Crystal Mine"),
    "3": BuildingItem(3, "Deuterium Synthesizer"),
    "4": BuildingItem(4, "Solar Plant"),
    "12": BuildingItem(12, "Fusion Reactor"),
    "102": BuildingItem(22, "Metal Storage"),
    "22": BuildingItem(23, "Crystal Storage"),
    "23": BuildingItem(24, "Deuterium Tank")

}


class BuildingItem(Item): pass


class BuildingData(object):
    def __init__(self, building, level):
        self.building = building
        self.level = level


class Buildings(Scraper):
    def __init__(self, browser, config):
        super(Buildings, self).__init__(browser, config)
        self.general_client = General(browser, config)

    @staticmethod
    def parse_buildings(buildings):
        planet_buildings = {}
        count = 0
        for building_type in BuildingTypes:
            planet_buildings[building_type] = BuildingItem(buildings[count][0], buildings[count][1])
            count += 1
        return planet_buildings

    def get_buildings(self, planet):
        self.logger.info('Getting buildings data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('resources', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        building_buttons = soup(attrs={'class': "detail_button"})

        buildings = []
        for building_button in building_buttons:
            building_data = self.get_building_data_from_button(building_button)

            if building_data is not None:
                buildings.append(building_data)
        return buildings

    @staticmethod
    def get_building_data_from_button(building_button):
        """ Read the bulding data from the building button """

        id = building_button['ref']
        building_data = BUILDINGS_DATA.get(id)

        # ensures that execution will not break if there is a new item
        if building_data is not None:
            try:
                building_info = "".join(building_button.find("span", {"class": "level"})
                                        .findAll(text=True, recursive=False)[1])
            # If we get an exception here it means the building is in construction mode, so we
            # the info we need will be at index 0
            except IndexError:
                building_info = "".join(building_button.find("span", {"class": "level"})
                                        .findAll(text=True, recursive=False)[0])

            level = int(re.sub("[^0-9]", "", building_info))
            return ItemAction(BuildingItem(building_data.id, building_data.name), level)
        else:
            return None

    def get_weaker_planet(self, planets=None):
        if planets is None:
            planets = self.general_client.get_planets()

        planet_sum_buildings = []
        totals = []

        for planet in planets:
            buildings_sum = sum([bld.amount for bld in self.get_buildings(planet)])
            planet_sum_buildings.append((planet, buildings_sum))
            totals.append(buildings_sum)

        weaker_planets = [planet_sum[0]
                          for planet_sum
                          in planet_sum_buildings
                          if planet_sum[1] == min(totals)]

        weaker_planet = next(iter(weaker_planets), None)
        return weaker_planet

    def get_available_building_for_planet(self, planet):
        """ Returns the first structure on planet that has enough resources to be built """

        buildings = self.get_available_buildings_for_planet(planet)
        building = next(iter(buildings), None)

        return building

    def get_available_buildings_for_planet(self, planet):
        """ Returns the the structures on planet that has enough resources to be built """

        url = self.url_provider.get_page_url('resources', planet)
        resp = self.open_url(url)

        soup = BeautifulSoup(resp.read(), "lxml")
        build_images = soup.findAll("a", {"class": "fastBuild tooltip js_hideTipOnMobile"})

        buildings = []

        for build_image in build_images:
            parent_block = build_image.parent
            building_btn = parent_block.find("a", {"id": "details"})
            building = self.get_building_data_from_button(building_btn)
            if building is not None:
                buildings.append(building.item)

        return buildings

    def build_structure(self, building_data, planet):
        if self.is_in_construction_mode(planet):
            self.logger.info('Planet %s is already in construction mode' % planet.name)
            return
        else:
            self.logger.info('Building %s on planet %s' % (building_data.name, planet.name))
            self.build_structure_item(building_data)

    def build_structure_item(self, building_data, planet=None):
        """
            Building structure to planet,
            it doesn't need the planet parameter if the browser
            is already at the resources page of the planet
        """

        if planet is not None:
            url = self.url_provider.get_page_url('resources', planet)
            self.open_url(url)

        self.create_control("form", "text", "menge", "1")
        self.create_control("form", "text", "type", str(building_data.id))
        self.create_control("form", "text", "modus", "1")

        self.logger.info("Submitting form")
        self.submit_request()

    def is_in_construction_mode(self, planet=None):
        """
        Check if the planet is in construction mode
        :param planet: planet to check
        :return: True if the planet is in construction mode, otherwise returns False
        """

        url = self.url_provider.get_page_url('resources', planet)
        resp = self.open_url(url)
        soup = BeautifulSoup(resp.read(), "lxml")
        # if the planet is in construction mode there shoud be a div with the
        # class construction
        return soup.find("div", {"class": "construction"}) != None
