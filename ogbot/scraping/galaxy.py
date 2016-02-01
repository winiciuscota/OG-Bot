import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urllib
from enum import Enum
from scraper import Scraper

class Galaxy(Scraper):

    def get_planets(self, galaxy, system):
        """
        Get planets in the given galaxy and system
        """
        self.logger.info('Getting data from (%s:%s)' % (galaxy, system))
        url = self.url_provider.get_page_url('galaxyContent')
        data = urllib.urlencode({'galaxy': galaxy, 'system': system})
        res = self.open_url(url, data).read()
        
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
            
            player_rank = self.get_rank(soup, player_name)
            planets.append(Planet(planet_name.strip(), planet_coordinates, player_name, player_state, player_rank))

        return planets

    def get_rank(self, soup, player_name):
        rank_nodes = soup.findAll("li", {"class" : "rank"})

        player_rank_node_match = [rank_node 
                                 for rank_node 
                                 in rank_nodes 
                                 if player_name in rank_node.parent.parent.text]

        if len(player_rank_node_match) == 0:
            return 0
        else:
            player_rank_node = player_rank_node_match[0]
            player_rank = int(player_rank_node.find("a").text.strip())
            return player_rank

class PlayerState(Enum):
    Active = 1
    Inactive = 2
    Vacation = 3

class Planet(object):
    def __init__(self, name, coordinates, player_name, player_state, player_rank):
        self.name = name
        self.coordinates = coordinates
        self.player_name = player_name
        self.player_state = player_state
        self.player_rank = player_rank

    def __str__(self):
        str = "Planet: %s, Coordinates: %s, Player %s (%s)(%d)" % (self.name,
         self.coordinates, self.player_name, self.player_state, self.player_rank)
        return str
        
    
