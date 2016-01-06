import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging

class Hangar:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_planets(self, galaxy, solar_system):
        """
        Get planets in the given galaxy and solar_system
        """
        self.logger.info('Getting galaxy data')
        url = self.url_provider.get_page_url('galaxy', planet)
        res = self.br.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("td", { "class" : "planetname " })
        planets = []
        for ref in refs:
            table_row = ref.parent
            planet_position = row.find("td", { "class" : "position js_no_action "}).text
            planet_name = ref.text
            # first we will search for active players
            player_name_node = table_row.find("td", { "class" : "status_abbr_active"})
            if player_name_node != None :
                player_name = player_name_node.text
            else :
                player_name_node = table_row.find("td", { "class" : "status_abbr_longinactive"})

            planets.append(Planet(planet_name, planet_position, galaxy, solar_system, planet_position))

        defenses = map(tuple, map(util.sanitize, [filter(None, i) for i in defenses]))
        return defenses

class Planet(object):
    def __init__(self, name, galaxy, solar_system, position, player_name = None, player_inactive = None):
        self.name = name
        self.galaxy = galaxy
        self.solar_system = solar_system
        self.position = position
        self.player_name = player_name
        self.player_inactive = player_inactive

    def __str__(self):
        return "%s (%d, %d, %d)" % (self.name, self.galaxy, self.solar_system, self.position)
