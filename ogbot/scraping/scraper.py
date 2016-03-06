import util
import logging
import mechanize
from enum import Enum

class Scraper(object):
    """Base class for scraper classes"""

    def __init__(self, browser, config):
        self.config = config
        self.url_provider = util.UrlProvider(self.config.universe)
        self.logger = logging.getLogger('OGBot')
        self.browser = browser

        self.attempts = 3
        self.timeout = 30.0
        self.ships = {
            "lf" : Ship(204, "Light Fighter"),
            "hf" : Ship(205, "Heavy Fighter"),
            "cr" : Ship(206, "Cruiser"),
            "bs" : Ship(207, "Battle Ship"),
            "cs" : Ship(207, "Colony Ship"),
            "sg" : Ship(202, "Small Cargo Ship"),
            "lg" : Ship(203, "Large Cargo Ship"),
            "ep" : Ship(210, "Espionage Probe")
        }
        self.missions = {
            "expedition" : 15,
            "colonization" : 7,
            "recycle" : 8,
            "transport" : 3,
            "transfer" : 4,
            "spy" : 6,
            "defend" : 5,
            "attack" : 1,
            "allianceAttack" : 2,
            "destroyStar" : 9
        }

    def open_url(self, url, data = None):
        """Open url, make up to 3 retrys"""
        for attempt in range(0, self.attempts):
            try:
                res = self.browser.open(url, data, self.timeout)
                return res
            except mechanize.URLError:
                self.logger.warning("URLError opening url, trying again for the %dth time" % (attempt + 1))
        
        #If is unable to connect quit the bot
        self.logger.error("Unable to comunicate with the server, exiting the bot")
        exit()

    def submit_request(self):
        """Submit browser, make up to 3 retrys"""
        for attempt in range(0, self.attempts):
            try:
                res = self.browser.submit()
                return res
            except mechanize.URLError:
                self.logger.warning("URLError submitting form, trying again for the %dth time" % (attempt + 1))
        
        #If is unable to connect quit the bot
        self.logger.error("Unable to comunicate with the server, exiting the bot")
        exit()

def sanitize(t):
    for i in t:
        try:
            yield int(i)
        except ValueError:
            yield i

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

    def empty(self):
        return self.metal == 0 and self.crystal == 0 and self.deuterium == 0

class Planet(object):
    def __init__(self, name, link, coordinates):
        self.name = name
        self.link = link
        self.coordinates = coordinates

    def __str__(self):
        return "[Planet: %s, Link: %s, Coordinates: %s]" % (self.name, self.link, self.coordinates)

class FleetResult(Enum):
    Success = 1
    WrongParameters = 2
    NoAvailableShips = 3

class Ship(object):
    def __init__(self, id, name, amount = None):
        self.name = name
        self.id = id
        self.amount = amount

    def __str__(self):
        return "[Description: %s, Id: %s%s ]" % (
            self.name, self.id, ", Amount: %s" if self.amount != None else "")


