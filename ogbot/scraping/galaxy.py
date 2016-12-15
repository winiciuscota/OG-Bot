from bs4 import BeautifulSoup
import urllib
from scraper import *
from ast import literal_eval
import re


class Galaxy(Scraper):
    def get_planets(self, galaxy, system):
        """
        Get planets in the given galaxy and system
        """
        self.logger.info('Getting data from system %s:%s' % (galaxy, system))
        url = self.url_provider.get_page_url('galaxyContent')
        data = urllib.urlencode({'galaxy': galaxy, 'system': system})
        res = self.open_url(url, data).read()

        # For some reason the server is retrieving a file full of escaped quotes,
        # So we need to replace the spaced quotes for normal quotes
        res2 = res.replace('\\"', '"')

        soup = BeautifulSoup(self.strip_text(res2), "lxml")

        table = soup.find("table", {"id": "galaxytable"})

        if table is None:
            self.logger.error("Invalid response from server, could not find #galaxytable")
            return []

        table_rows = table.findAll("tr", {"class": "row"})
        planets = []

        for table_row in table_rows:

            # skip empty table rows
            if "empty_filter" in table_row.get("class"):
                continue

            planet_name = self.strip_text(table_row(attrs={'class': "planetname"})[0].text)
            planet_position = self.strip_text(table_row.find('td', {'class': "position"}).text)
            planet_coordinates = ":".join([galaxy, system, planet_position])
            player_name_data = table_row(attrs={'class': "playername"})[0]
            player_name_heading = table_row.find('h1')
            if player_name_heading is None:
                continue
            player_name = player_name_heading.find('span').text

            # Set player state
            player_name_classes = player_name_data.get("class")

            if 'longinactive' in player_name_classes:
                player_state = PlayerState.Inactive

            elif 'vacationlonginactive' in player_name_classes or 'vacation' in player_name_classes:
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
            s = re.findall('^\d*', player_rank_string)
            player_rank = int(s[0] if s[0] else "-1")
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
