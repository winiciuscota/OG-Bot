import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urllib

class Galaxy:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_planets(self, galaxy, system):
        """
        Get planets in the given galaxy and system
        """
        self.logger.info('Getting galaxy data')
        url = self.url_provider.get_page_url('galaxyContent')
        self.logger.info('Galaxy content url is: %s' % url)
        data = urllib.urlencode({'galaxy': galaxy, 'system': system})
        res = self.browser.open(url, data=data)
        soup = BeautifulSoup(res.read())

        nodes = soup.findAll("td", {"class" : "planetname "})
        table_rows = [node.parent for node in nodes]

        planets = []
        for table_row in table_rows:
            planet_name = table_row.find("td", { "class" : "planetname"}).text
            planet_position = int(table_row.find("td", {"class" : "position js_no_action "}).text)
            # first we will search for active player
            player_name_node = table_row.find("span", { "class" : "status_abbr_active"})
            if player_name_node != None :
                player_name = player_name_node.text
            else :
                # then search for inactive player
                player_name_node = table_row.find("span", { "class" : "status_abbr_longinactive"})
            planets.append(Planet(planet_name, planet_position, int(galaxy), int(system), planet_position))

        return planets


class Planet(object):
    def __init__(self, name, galaxy, system, position, player_name = None, player_inactive = None):
        self.name = name
        self.galaxy = galaxy
        self.system = system
        self.position = position
        self.player_name = player_name
        self.player_inactive = player_inactive

    def __str__(self):
        return "%s (%d, %d, %d)" % (self.name, self.galaxy, self.system, self.position)
