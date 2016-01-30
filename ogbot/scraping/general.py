import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urlparse
import datetime

class General:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def log_index_page(self):
        """Logs the index page, used for test purposes"""
        url = self.url_provider.get_page_url('overview')
        res = util.open_url(self.browser, url)
        self.logger.info(res.read())

    def get_game_datetime(self):
        url = self.url_provider.get_page_url('overview')
        res = util.open_url(self.browser, url)
        soup = BeautifulSoup(res.read(), "lxml")

        datetime_data = soup.find("li", {"class": "OGameClock"}).text
        game_datetime = datetime.datetime.strptime(datetime_data, "%d.%m.%Y %H:%M:%S")
        return game_datetime

    def get_resources(self, planet):
        self.logger.info('Getting resources data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('resources', planet)
        res = util.open_url(self.browser, url)
        soup = BeautifulSoup(res.read())

        resources = []
        metal = int(soup.find(id='resources_metal').text.replace('.',''))
        crystal = int(soup.find(id='resources_crystal').text.replace('.',''))
        deuterium = int(soup.find(id='resources_deuterium').text.replace('.',''))
        energy = int(soup.find(id='resources_energy').text.replace('.',''))

        return Resources(metal, crystal, deuterium, energy)

    def get_planets(self):
        self.logger.info('Getting planets')
        url = self.url_provider.get_page_url('resources')
        res = util.open_url(self.browser, url)
        soup = BeautifulSoup(res.read())
        planets = []
        current_planet_id = soup.find("meta", { "name" : "ogame-planet-id"})['content']
        current_planet_name = soup.find("meta", { "name" : "ogame-planet-name"})['content']
        current_planet_koords = soup.find("meta", { "name" : "ogame-planet-coordinates"})['content']
        current_planet = Planet(current_planet_name, current_planet_id, current_planet_koords)
        planets.append(current_planet)
        links = soup.findAll("a", { "class" : "planetlink tooltipRight js_hideTipOnMobile" })
        other_planets = [ Planet((str(link.find("span", {"class" : "planet-name  "}).contents[0])),
                            urlparse.parse_qs(link['href'])['cp'][0],
                            self.parse_coordinates(str(link.find("span", {"class" : "planet-koords  "}).contents[0])))
                            for link in links]
        if len(other_planets) > 1:
            planets.extend(other_planets)
        return planets

    def parse_coordinates(self, coords):
        return coords.replace('[', '').replace(']', '')



class Resources(object):
    def __init__(self, metal, crystal, deuterium = 0, energy = 0):
        self.metal = metal
        self.crystal = crystal
        self.deuterium = deuterium
        self.energy = energy

    def __str__(self):
        result = []
        if self.metal != 0:
            result.append("Metal: %s" % self.metal)
        if self.crystal != 0:
            result.append("Crystal: %s" % self.crystal)
        if self.deuterium != 0:
            result.append("Deuterium: %s" % self.deuterium)
        if self.energy != 0:
            result.append("Energy: %s" % self.energy)
        return ', '.join(result)

    def total(self):
        return self.metal + self.crystal + self.deuterium

class Planet(object):
    def __init__(self, name, link, coordinates):
        self.name = name
        self.link = link
        self.coordinates = coordinates

    def __str__(self):
        return "[Planet: %s, Link: %s, Coordinates: %s]" % (self.name, self.link, self.coordinates)
