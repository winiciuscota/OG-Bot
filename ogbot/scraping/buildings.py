import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urlparse
from enum import Enum
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
    "ms": BuildingItem(102, "Metal Storage"),
    "cm": BuildingItem(22, "Crystal Storage"),
    "dt": BuildingItem(23, "Deuterium Tank"),

    "1": BuildingItem(1, "Metal Mine"),
    "2": BuildingItem(2, "Crystal Mine"),
    "3": BuildingItem(3, "Deuterium Synthesizer"),
    "4": BuildingItem(4, "Solar Plant"),
    "12": BuildingItem(12, "Fusion Reactor"),
    "102": BuildingItem(102, "Metal Storage"),
    "22": BuildingItem(22, "Crystal Storage"),
    "23": BuildingItem(23, "Deuterium Tank")

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

    def parse_buildings(self, buildings):
        planet_buildings = {}
        count = 0
        for building_type in BuildingTypes:
            planet_buildings[building_type] = BuildingItem(buildings[count][0], buildings[count][1])
            count += 1
        return planet_buildings

    def get_buildings(self, planet):
        self.logger.info('Getting buildings data')
        url = self.url_provider.get_page_url('resources', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        building_buttons = soup(attrs={'class': "detail_button"})

        buildings = []
        for building_button in building_buttons:
            id = building_button['ref']
            building_data = BUILDINGS_DATA.get(id)

            # ensures that execution will not break if there is a new item
            if building_data != None:
                try:
                    building_info = "".join(building_button.find("span", {"class": "level"})
                                          .findAll(text=True, recursive=False)[1])
                # If we get an exception here it means the building is in construction mode, so we
                # the info we need will be at index 0
                except IndexError:
                    building_info = "".join(building_button.find("span", {"class": "level"})
                                          .findAll(text=True, recursive=False)[0])

                level = int(re.sub("[^0-9]", "", building_info))
                buildings.append(ItemAction(BuildingItem(building_data.id, building_data.name), level))
        return buildings


    def get_weaker_planet(self):
        planets = self.general_client.get_planets()
        planet_sum_buildings = []
        totals = []

        for planet in planets:
            buildings_sum = sum([bld.amount for bld in self.get_buildings(planet)])
            planet_sum_buildings.append((planet, buildings_sum))
            totals.append(buildings_sum)

        weaker_planets = [planet_sum[0] for planet_sum in planet_sum_buildings if planet_sum[1] == min(totals)]
        weaker_planet = next(iter(weaker_planets), None)
        return weaker_planet

    def auto_build_structure(self, planet):
        if self.construction_mode(planet):
            self.logger.info('Planet is already in construction mode')
            return
        else:
            resources = self.general_client.get_resources(planet)
            buildings = self.get_buildings(planet)

            crystal_mine_level = buildings.get(BuildingTypes.CrystalMine).level
            metal_mine_level = buildings.get(BuildingTypes.MetalMine).level
            deuterium_synthesizer_level = buildings.get(BuildingTypes.DeuteriumSynthesizer).level
            metal_storage_level = buildings.get(BuildingTypes.MetalStorage).level
            crystal_storage_level = buildings.get(BuildingTypes.CrystalStorage).level
            deuterium_tank_level = buildings.get(BuildingTypes.DeuteriumTank).level

            if resources.energy < 0:
                self.build_structure_item(BuildingTypes.SolarPlant, planet)
            else:
                if crystal_mine_level - metal_mine_level > 2:
                    if crystal_storage_level == 0 or crystal_mine_level / crystal_storage_level > 3:
                        self.build_structure_item(BuildingTypes.CrystalStorage, planet)
                    else:
                        self.build_structure_item(BuildingTypes.CrystalMine, planet)
                else:
                    if deuterium_synthesizer_level - metal_mine_level > 5:
                        if deuterium_tank_level == 0 or deuterium_synthesizer_level / deuterium_tank_level > 3:
                            self.build_structure_item(BuildingTypes.DeuteriumTank, planet)
                        else:
                            self.build_structure_item(BuildingTypes.DeuteriumSynthesizer, planet)
                    else:
                        if metal_storage_level == 0 or metal_mine_level / metal_storage_level > 3:
                            self.build_structure_item(BuildingTypes.MetalStorage, planet)
                        else:
                            self.build_structure_item(BuildingTypes.MetalMine, planet)

    def build_structure(self, building_type, planet):
        if self.construction_mode(planet):
            self.logger.info('Planet is already in construction mode')
            return
        else:
            self.build_structure_item(building_type.value, planet)

    def build_structure_item(self, building_data, planet = None):
        self.logger.info('Building %s on planet %s' % (type, building_data.item.data))
        self.browser.select_form(name='form')
        self.browser.form.new_control('text','menge',{'value':'1'})
        self.browser.form.fixup()
        self.browser['menge'] = '1'

        self.browser.form.new_control('text','type',{'value': str(building_data)})
        self.browser.form.fixup()
        self.browser['type'] = str(building_data)

        self.browser.form.new_control('text','modus',{'value':'1'})
        self.browser.form.fixup()
        self.browser['modus'] = '1'

        self.logger.info("Submitting form")
        self.submit_request()

    def construction_mode(self, planet = None):
        url = self.url_provider.get_page_url('resources', planet)
        self.logger.info('Opening url %s' % url)
        resp = self.open_url(url)
        soup = BeautifulSoup(resp.read())
        # if the planet is in construction mode there shoud be a div with the
        # class construction
        return soup.find("div", {"class" : "construction"}) != None
