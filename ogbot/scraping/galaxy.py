from bs4 import BeautifulSoup
import urllib
from enum import Enum
from scraper import *
from ast import literal_eval


class Galaxy(Scraper):
    def get_planets(self, galaxy, system):
        """
        Get planets in the given galaxy and system
        """
        self.logger.info('Getting data from system %s:%s' % (galaxy, system))
        url = self.url_provider.get_page_url('galaxyContent')
        data = urllib.urlencode({'galaxy': galaxy, 'system': system})
        res = self.open_url(url, data).read()
        res2 = str(literal_eval(res))
        soup = BeautifulSoup(res2, "lxml")

        nodes = soup.findAll("td", {"class": 'planetname'})
        table_rows = [node.parent for node in nodes]

        planets = []

        for table_row in table_rows:

            planet_name = self.strip_text(table_row(attrs={'class': "planetname"})[0].text)
            planet_coordinates_data = table_row(attrs={'id': "pos-planet"})[0].text
            planet_coordinates = self.strip_text(str(planet_coordinates_data).split(']')[0])
            # player_name_data = table_row(attrs={'class': "playername"})[0]
            # player_name_heading = player_name_data.find('h1')
            player_name_data = None
            player_name_heading = table_row.find('h1')
            if player_name_heading is None:
                continue
            player_name = player_name_heading.find('span').text
            player_state_data = player_name_data(attrs={'class': "status"})[0].text

            # Set player state
            if '(I)' in player_state_data:
                player_state = PlayerState.Inactive
            elif '(m I)' in player_state_data or '(m)' in player_state_data:
                player_state = PlayerState.Vacation
            else:
                player_state = PlayerState.Active

            player_rank = self.get_rank(soup, player_name)
            planets.append(Planet(planet_name, planet_coordinates, player_name, player_state, player_rank))

        return planets

    @staticmethod
    def strip_text(text):
        return text.replace("\\n", '').strip("u' [ ]")

    @staticmethod
    def get_rank(soup, player_name):
        rank_nodes = soup.findAll("li", {"class": "rank"})

        player_rank_node_match = [rank_node
                                  for rank_node
                                  in rank_nodes
                                  if player_name in rank_node.parent.parent.text]

        if len(player_rank_node_match) == 0:
            return 0
        else:
            player_rank_node = player_rank_node_match[0]
            player_rank_string = player_rank_node.find("a").text.strip()
            player_rank = int(player_rank_string if player_rank_string else "-1")
            return player_rank


class Planet(object):
    def __init__(self, name, coordinates, player_name, player_state, player_rank):
        self.name = name
        self.coordinates = coordinates
        self.player_name = player_name
        self.player_state = player_state
        self.player_rank = player_rank

    def __str__(self):
        description = "Planet: %s, Coordinates: %s, Player %s (%s)(%d)" % (self.name,
                                                                           self.coordinates, self.player_name,
                                                                           self.player_state, self.player_rank)
        return description
