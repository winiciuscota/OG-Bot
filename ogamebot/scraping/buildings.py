import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urlparse
from enum import Enum
from general import General


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

class Building(object):
    def __init__(self, name, level):
        self.name = name
        self.level = level

class Buildings:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser
        self.general_client = General(browser, universe)

    def parse_buildings(self, buildings):
        planet_buildings = {}
        count = 0
        for building_type in BuildingTypes:
            planet_buildings[building_type] = Building(buildings[count][0], buildings[count][1])
            count += 1
        return planet_buildings

    def get_buildings(self, planet):
        self.logger.info('Getting buildings data')
        url = self.url_provider.get_page_url('resources', planet)
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })
        res = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                res.append( tuple(shipData.split('\n')))

        parsed_res = map(tuple, map(util.sanitize, [filter(None, i) for i in res]))
        buildings = self.parse_buildings(parsed_res)
        return buildings

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

    def build_structure(self, type, planet):
        if self.construction_mode(planet):
            self.logger.info('Planet is already in construction mode')
            return
        else:
            self.build_structure_item(type.value, planet)

    def build_structure_item(self, type, planet = None):
        self.logger.info('Building %s on planet %s' %(type, planet.name))
        self.browser.select_form(name='form')
        self.browser.form.new_control('text','menge',{'value':'1'})
        self.browser.form.fixup()
        self.browser['menge'] = '1'

        self.browser.form.new_control('text','type',{'value': str(type)})
        self.browser.form.fixup()
        self.browser['type'] = str(type)

        self.browser.form.new_control('text','modus',{'value':'1'})
        self.browser.form.fixup()
        self.browser['modus'] = '1'

        self.logger.info("Submitting form")
        self.browser.submit()

    def construction_mode(self, planet = None):
        url = self.url_provider.get_page_url('resources', planet)
        self.logger.info('Opening url %s' % url)
        resp = self.browser.open(url)
        soup = BeautifulSoup(resp.read())
        # if the planet is in construction mode there shoud be a div with the class construction
        return soup.find("div", {"class" : "construction"}) != None
