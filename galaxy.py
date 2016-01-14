import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urllib
from enum import Enum

class Galaxy:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_planets(self, galaxy, system):
        """
        Get planets in the given galaxy and system
        """
        self.logger.info('Getting data from (%s:%s)' % (galaxy, system))
        url = self.url_provider.get_page_url('galaxyContent')
        self.logger.info('Galaxy content url is: %s' % url)
        data = urllib.urlencode({'galaxy': galaxy, 'system': system})
        res = self.browser.open(url, data=data)
        soup = BeautifulSoup(res.read())

        nodes = soup.findAll("td", {"class" : "planetname "})
        table_rows = [node.parent for node in nodes]

        planets = []
        player_name = ''
        player_inactive = ''

        for table_row in table_rows:
            planet_name = table_row.find("td", { "class" : "planetname"}).text.strip()
            planet_position = table_row.find("td", {"class" : "position js_no_action "}).text
            planet_coordinates = ":".join([galaxy, system, planet_position])

            # first we will search for active player
            player_name_node = table_row.find("span", { "class" : "status_abbr_active"})

            if player_name_node != None :
                player_name = player_name_node.text.strip()
                player_inactive = PlayerState.Active
            else :
                player_name_node = table_row.find("span", { "class" : "status_abbr_honorableTarget"})
            if player_name_node != None:
                player_name = player_name_node.text.strip()
                player_inactive = PlayerState.Active
            else :
                # then search for inactive player
                player_name_node = table_row.find("span", { "class" : "status_abbr_longinactive"})
                if player_name_node != None and len(player_name_node.text) > 1:
                    player_name = player_name_node.text.strip()
                    player_inactive = PlayerState.Inactive
                else:
                    # last look for players on vacation
                    player_name_node = table_row.find("span", { "class" : "status_abbr_vacation"})
                    if player_name_node != None and len(player_name_node.text) > 1:
                        player_name = player_name_node.text
                        player_inactive = PlayerState.Vacation

            planets.append(Planet(planet_name.strip(), planet_coordinates, player_name, player_inactive))

        return planets

class PlayerState(Enum):
    Active = 1
    Inactive = 2
    Vacation = 3

class Planet(object):
    def __init__(self, name, coordinates, player_name, player_state):
        self.name = name
        self.coordinates = coordinates
        self.player_name = player_name
        self.player_state = player_state

    def __str__(self):
        str = "Planet: %s, Coordinates: %s, Player %s (%s)" % (self.name,
         self.coordinates, self.player_name, self.player_state)
        return str
