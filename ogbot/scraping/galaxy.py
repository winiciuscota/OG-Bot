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
        data = urllib.urlencode({'galaxy': galaxy, 'system': system})
        res = self.browser.open(url, data=data).read()
        
        soup = BeautifulSoup(res, "lxml")

        nodes = soup.findAll("td", {"class" : "planetname "})
        table_rows = [node.parent for node in nodes]

        planets = []
        player_name = ''

        for table_row in table_rows:
            table_data_nodes = table_row.findAll("td")
            planet_position = table_data_nodes[1].text.strip()
            planet_name = table_data_nodes[3].text.strip()
            planet_coordinates = ":".join([galaxy, system, planet_position])
            
            player_name_data = table_data_nodes[7].text.strip()
            player_name_info = player_name_data.replace("\n", ',').replace(":", ",").split(',')
            player_name = player_name_info[0].strip()
            
            #Set player state
            if '(I)' in player_name_data:
                player_state = PlayerState.Inactive
            elif '(m I)' in player_name_data or '(m)' in player_name_data:
                player_state = PlayerState.Vacation
            else:
                player_state = PlayerState.Active
                
            planets.append(Planet(planet_name.strip(), planet_coordinates, player_name, player_state))

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
        
    
