﻿import util
import logging
import mechanize
from enum import Enum


class Scraper(object):
    """Base class for scraper classes"""

    def __init__(self, browser, config):
        self.config = config
        self.url_provider = util.UrlProvider(self.config.universe, self.config.country)
        self.logger = logging.getLogger('OGBot')
        self.browser = browser

        self.attempts = 3
        self.timeout = 30.0
        self.SHIPS_DATA = {
            "lf": ShipItem(204, "Light Fighter"),
            "hf": ShipItem(205, "Heavy Fighter"),
            "cr": ShipItem(206, "Cruiser"),
            "bs": ShipItem(207, "Battle Ship"),
            "cs": ShipItem(208, "Colony Ship"),
            "sg": ShipItem(202, "Small Cargo Ship"),
            "lg": ShipItem(203, "Large Cargo Ship"),
            "ep": ShipItem(210, "Espionage Probe"),
            "bc": ShipItem(215, "Battlecruiser"),
            "b": ShipItem(211, "Bomber"),
            "d": ShipItem(213, "Destroyer"),
            "ds": ShipItem(214, "Deathstar"),
            "r": ShipItem(209, "Recycler"),
            "ss": ShipItem(212, "Solar Satellite"),

            "204": ShipItem(204, "Light Fighter"),
            "205": ShipItem(205, "Heavy Fighter"),
            "206": ShipItem(206, "Cruiser"),
            "207": ShipItem(207, "Battle Ship"),
            "208": ShipItem(208, "Colony Ship"),
            "202": ShipItem(202, "Small Cargo Ship"),
            "203": ShipItem(203, "Large Cargo Ship"),
            "210": ShipItem(210, "Espionage Probe"),
            "215": ShipItem(215, "Battlecruiser"),
            "211": ShipItem(211, "Bomber"),
            "213": ShipItem(213, "Destroyer"),
            "214": ShipItem(214, "Deathstar"),
            "209": ShipItem(209, "Recycler"),
            "212": ShipItem(212, "Solar Satellite"),
        }

        self.SHIPS_SIZE = {
            "sg": 5000,
            "lg": 25000,
            "r": 20000,

            "202": 5000,
            "203": 25000,
            "209": 20000
        }

        self.missions = {
            "expedition": 15,
            "colonization": 7,
            "recycle": 8,
            "transport": 3,
            "transfer": 4,
            "spy": 6,
            "defend": 5,
            "attack": 1,
            "allianceAttack": 2,
            "destroyStar": 9
        }

        self.mission_types = {
            15 : "expedition",
            7 : "colonization",
            8 : "recycle",
            3 : "transport",
            4 : "transfer",
            6 : "spy",
            5 : "defend",
            1 : "attack",
            2 : "allianceAttack",
            9 : "destroyStar"
        }

    def open_url(self, url, data=None):
        """
        Redirect to the url, makes up to 3 attempts
        :param url: Url to redirect to
        :param data: Additional data to send in the get request
        """
        for attempt in range(0, self.attempts):
            try:
                res = self.browser.open(url, data, self.timeout)

                # Detect authentication loss
                if url.startswith(self.url_provider.main_url) \
                    and not res.geturl().startswith(self.url_provider.main_url):
                    self.logger.error('Authentication lost, exiting the bot')
                    exit()

                return res

            except mechanize.URLError:
                self.logger.warning("URLError opening url, trying again for the %dth time" % (attempt + 1))

        # If is unable to connect quit the bot
        self.logger.error("Unable to communicate with the server, exiting the bot")
        exit()

    def submit_request(self):
        """
        Submit form, makes up to 3 attempts
        """
        for attempt in range(0, self.attempts):
            try:
                res = self.browser.submit()
                return res

            except mechanize.URLError:
                self.logger.warning("URLError submitting form, trying again for the %dth time" % (attempt + 1))

        # If is unable to connect quit the bot
        self.logger.error("Unable to communicate with the server, exiting the bot")
        exit()

    def get_current_url(self):
        """
        :return: The url where the browser is in
        """
        return self.browser.geturl()

    def create_control(self, form_id, control_type, control_name, control_value):
        """
        Create a new control in the specified form
        :param form_id: id of the form in which the control will be created
        :param control_type: type of the control to be created(i.e.: 'text')
        :param control_name: name of the control to be created
        :param control_value: value of the control to be created
        :return:
        """
        self.browser.select_form(name=form_id)
        self.browser.form.new_control(control_type, control_name, {'value': ''})
        self.browser.form.fixup()
        self.browser[control_name] = control_value


def sanitize(t):
    for i in t:
        try:
            yield int(i)
        except ValueError:
            yield i


class Resources(object):
    def __init__(self, metal, crystal, deuterium=0, energy=0):
        self.metal = metal
        self.crystal = crystal
        self.deuterium = deuterium
        self.energy = energy

    def __sub__(self, other):
        result_metal = self.metal - other.metal
        result_crystal = self.crystal - other.crystal
        result_deuterium = self.crystal - other.crystal

        return Resources(result_metal, result_crystal, result_deuterium)

    def __lt__(self, other):

        return self.metal < other.metal \
               and self.crystal < other.crystal \
               and self.deuterium < other.deuterium

    def __str__(self):
        result = []
        if self.metal != 0:
            result.append("Metal: %s" % "{:,.0f}".format(self.metal))
        if self.crystal != 0:
            result.append("Crystal: %s" % "{:,.0f}".format(self.crystal))
        if self.deuterium != 0:
            result.append("Deuterium: %s" % "{:,.0f}".format(self.deuterium))
        if self.energy != 0:
            result.append("Energy: %s" % "{:,.0f}".format(self.energy))
        return ', '.join(result)

    def total(self):
        return self.metal + self.crystal + self.deuterium

    def empty(self):
        return self.metal == 0 and self.crystal == 0 and self.deuterium == 0

    def sum(self, resources):
        self.metal += resources.metal
        self.crystal += resources.crystal
        self.deuterium += resources.deuterium

    def times(self, number):
        return Resources(self.metal * number, self.crystal * number, self.deuterium * number)

    def get_points(self):
        return sum([self.metal, self.crystal, self.deuterium])


class Planet(object):
    def __init__(self, name, link, spaceUsed, spaceMax, coordinates, resources=None, defenses=None, fleet=None, research=None):
        """
        :param name: Planet name
        :param link: Planet link
        :param coordinates: Planet coordinates
        :param resources: Resources on the planet
        :param defenses: Defenses on the planet
        :param fleet: Fleet on the planet
        """
        self.name = name
        self.link = link
        self.coordinates = coordinates
        self.resources = resources
        self.defenses = defenses
        self.fleet = fleet
        self.research = research
        self.safe = True
        self.spaceUsed = spaceUsed
        self.spaceMax = spaceMax
        self.moon = None
        self.isMoon = False
        self.hasMoon = False

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "[Planet: %s, Link: %s, Coordinates: %s, Space: %d/%d, Moon: %s]" % (self.name, self.link, self.coordinates, self.spaceUsed, self.spaceMax, 'Yes' if self.isMoon else 'No')


class FleetResult(Enum):
    Success = 1
    WrongParameters = 2
    NoAvailableShips = 3
    NoAvailableSlots = 4


class Item(object):
    def __init__(self, item_id, name, cost=None):
        self.name = name
        self.id = item_id
        self.cost = cost

    def __str__(self):
        return "[Description: %s, Id: %s ]" % (self.name, self.id)


class ItemAction(object):
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount

    def __str__(self):
        return "[Description: %s, Id: %s, Amount: %s  ]" % (
            self.item.name, self.item.id, self.amount)


class ShipItem(Item):
    pass


class DefenseItem(Item):
    pass


class BuildingItem(Item):
    pass


class ResearchItem(Item):
    pass


class FleetMovement(object):
    def __init__(self, origin_coordinates, origin_name, destination_coordinates, destination_name, friendly,
                 arrival_time=None, countdown_time=None, mission='attack', isMoon=False):
        """
        :param origin_coordinates: Coordinates of the origin planet
        :param origin_name: Name of the origin planet
        :param destination_coordinates: Destination of the destination planet
        """
        self.origin_coords = origin_coordinates
        self.origin_name = origin_name
        self.destination_coords = destination_coordinates
        self.destination_name = destination_name
        self.friendly = friendly
        self.arrival_time = arrival_time
        self.countdown_time = countdown_time
        self.mission = mission
        self.isMoon = isMoon

    def __str__(self):
        return "%s fleet from planet %s(%s) to planet %s(%s) in %s with %s mission" % (("Friendly" if self.friendly else "Hostile"),
                                                                       self.origin_name, self.origin_coords,
                                                                       self.destination_name, self.destination_coords,
                                                                       self.countdown_time, self.mission)

    def get_count_down_time(self, arrival_time):
        game_time = self.general_client.get_game_datetime()
        return arrival_time - game_time


class PlayerState(Enum):
    Active = 1
    Inactive = 2
    Vacation = 3
