from bs4 import BeautifulSoup
import urlparse
import datetime
from scraper import *


class General(Scraper):
    def log_index_page(self):
        """Logs the index page, used for test purposes"""
        url = self.url_provider.get_page_url('overview')
        res = self.open_url(url)
        self.logger.info(res.read())

    def get_game_datetime(self):
        url = self.url_provider.get_page_url('overview')
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        datetime_data = soup.find("li", {"class": "OGameClock"}).text
        game_datetime = datetime.datetime.strptime(datetime_data, "%d.%m.%Y %H:%M:%S")
        return game_datetime

    def get_resources(self, planet):
        self.logger.debug('Getting resources data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('resources', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        resources = []
        metal = int(soup.find(id='resources_metal').text.replace('.', ''))
        crystal = int(soup.find(id='resources_crystal').text.replace('.', ''))
        deuterium = int(soup.find(id='resources_deuterium').text.replace('.', ''))
        energy = int(soup.find(id='resources_energy').text.replace('.', ''))

        return Resources(metal, crystal, deuterium, energy)

    def get_planets(self):
        self.logger.info('Getting planets')
        url = self.url_provider.get_page_url('resources')

        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        links = soup(attrs={'class': "planetlink"})

        planets = [Planet((str(link(attrs={'class': "planet-name"})[0].contents[0])),
                          urlparse.parse_qs(link['href'])['cp'][0],
                          parse_coordinates(str(link(attrs={'class': "planet-koords"})[0].contents[0])))
                   for link in links]

        return planets

        # def get_planets_overview(self):
        #     planets = self.get_planets()
        #     defense_client = Defense(self.browser, self.config)
        #     hangar_client = Hangar(self.browser, self.config)
        #     buildings_client = Buildings(self.browser, self.config)
        #
        #     for planet in planets:
        #         planet.resources = self.get_resources(planet)
        #         planet.defenses = defense_client.get_defenses(planet)
        #         planet.fleet = hangar_client.get_ships(planet)
        #         planet.buildings = buildings_client.get_buildings(planet)
        #
        #     return planets


def parse_coordinates(coords):
    return coords.replace('[', '').replace(']', '')
