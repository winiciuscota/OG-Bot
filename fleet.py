from __future__ import division
import util
from mechanize import Browser
import mechanize
from bs4 import BeautifulSoup
import re
import logging
import urlparse
from enum import Enum
from general import General
import math

class Ship(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

class Fleet:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.general_client = General(browser, universe)
        self.browser = browser
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

        self.ships = {
            "lf" : Ship(204, "Light Fighter"),
            "hf" : Ship(205, "Heavy Fighter"),
            "cr" : Ship(206, "Cruiser"),
            "bs" : Ship(207, "Battle Ship"),
            "cs" : Ship(207, "Colony Ship"),
            "sg" : Ship(202, "Small Cargo Ship"),
            "lg" : Ship(203, "Large Cargo Ship")
        }


    def transport_resources(self, origin_planet, destination_planet, resources):
        planet_resources = self.general_client.get_resources(origin_planet)
        if planet_resources.metal < resources.metal:
            resources.metal = planet_resources.metal
        if planet_resources.crystal < resources.crystal:
            resources.crystal = planet_resources.crystal
        if planet_resources.deuterium < resources.deuterium:
            resources.deuterium = planet_resources.deuterium

        resources_count = resources.total()
        ships_count = int(math.ceil(resources_count / 25000))
        self.logger.info("Sending %d heavy cargos" % ships_count)

        self.send_fleet(origin_planet, destination_planet, resources, { self.ships.get('lg') : ships_count}, self.missions["transport"])

    def send_fleet(self, origin_planet, destination_planet, resources, ships, mission):
        """
        Missions:
            15 - Expedition,
            7 - Colonization,
            8 - Recycle,
            3 - Transport,
            4 - Transfer,
            6 - Spy,
            5 - Defend planet,
            1 - Attack,
            2 - Alliance attack,
            9 - Destroy star
        """

        if origin_planet.coordinates == destination_planet.coordinates:
            self.logger.error("Origin and destination are the same")
            return

        url = self.url_provider.get_page_url('fleet', origin_planet)
        self.logger.info('Opening fleet url: %s ' % url )
        resp = self.browser.open(url)

        try:
            self.browser.select_form(name='shipsChosen')
        except mechanize.FormNotFoundError:
            self.logger.error('The planet has no available ships')
            return

        # set ships to send
        soup = BeautifulSoup(resp.read())
        for ship, amount in ships.iteritems():
            self.browser["am" + str(ship.id)] = str(amount)
        self.browser.submit()

        # set target planet
        self.browser.select_form(name='details')
        self.browser["galaxy"] = destination_planet.coordinates.split(':')[0]
        self.browser["system"] = destination_planet.coordinates.split(':')[1]
        self.browser["position"] = destination_planet.coordinates.split(':')[2]
        self.browser.submit()

        # set mission and resouces to send
        self.browser.select_form(name='sendForm')
        self.browser.form.find_control('mission').readonly = False
        self.browser["mission"] = str(mission)
        self.browser["metal"] = str(resources.metal)
        self.browser["crystal"] = str(resources.crystal)
        self.browser["deuterium"] = str(resources.deuterium)
        self.browser.submit()
        self.logger.info("Sending %s with %s from planet %s to planet %s" %
            (self.get_ships_list(ships), resources, origin_planet.name, destination_planet.name))

    def get_ships_list(self, ships):
        return ", ".join([ str(ships.get(ship))  + ' ' + str(ship) for ship in ships])
