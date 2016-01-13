import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging


class Movement:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_fleet_movement(self):
        raise NotImplementedError
        url = self.url_provider.get_page_url('movement')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        movement_nodes = soup.findAll("div", { "class" : "fleetDetails detailsOpened" })
        for movement_node in movement_nodes:
            origin_planet_coords = movement_node.find("span", {"class": "originCoords"}).text
            origin_planet_name = movement_node.find("span", {"class": "originPlanet"}).text
            destination_planet = movement_node.find("span", {"class" : "destinationPlanet"})


class FleetMovement(object):
    def __init__(origin_coords, origin_name, target_coords, target_name, mission):
        self.origin_coords = origin_coords
        self.origin_name = origin_name
        self.target_coords = target_coords
        self.target_name = target_name
        self.mission = mission
