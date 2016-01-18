from __future__ import division
import util
from mechanize import Browser
import mechanize
from bs4 import BeautifulSoup
import re
import logging
import urlparse
from enum import Enum
import general
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
        self.general_client = general.General(browser, universe)
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
            "lg" : Ship(203, "Large Cargo Ship"),
            "ep" : Ship(210, "Espionage Probe")
        }

    def spy_planet(self, origin_planet, destination_planet):
        spy_probes_count = 5

        self.send_fleet(origin_planet, destination_planet.coordinates,
            self.missions["spy"], { self.ships.get('ep') : spy_probes_count})

    def attack_inactive_planet(self, origin_planet, target_planet):
        fleet = self.get_attack_fleet(target_planet)
        self.logger.info("Atacking planet %s from planet %s", target_planet.planet_name, origin_planet.name)
        result = self.send_fleet(origin_planet, target_planet.coordinates,
             self.missions["attack"], fleet)
        return result

    def transport_resources(self, origin_planet, destination_planet, resources):
        planet_resources = self.general_client.get_resources(origin_planet)
        if planet_resources.metal < resources.metal:
            resources.metal = planet_resources.metal
        if planet_resources.crystal < resources.crystal:
            resources.crystal = planet_resources.crystal
        if planet_resources.deuterium < resources.deuterium:
            resources.deuterium = planet_resources.deuterium

        fleet = self.get_tranport_fleet(resources)
        self.logger.info("Fleet: %s" % fleet)

        self.send_fleet(origin_planet, destination_planet.coordinates,
             self.missions["transport"], fleet, resources)

    def send_fleet(self, origin_planet, coordinates, mission, ships, resources = None):
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
        if resources == None:
            resources = general.Resources(0, 0)

        if origin_planet.coordinates == coordinates:
            self.logger.error("Origin and destination are the same")
            return FleetResult.WrongParameters

        url = self.url_provider.get_page_url('fleet', origin_planet)
        resp = self.browser.open(url)

        try:
            self.browser.select_form(name='shipsChosen')
        except mechanize.FormNotFoundError:
            self.logger.error('The planet has no available ships')
            return FleetResult.NoAvailableShips

        # set ships to send
        soup = BeautifulSoup(resp.read())
        for ship, amount in ships.iteritems():
            self.logger.info("Adding %d %s to the mission fleet" % (amount, ship.name))
            control_name = "am" + str(ship.id)
            control = self.browser.form.find_control(control_name)
            # If there is no available ships exit
            if control.readonly == False:
                self.browser[control_name] = str(amount)
            else:
                self.logger.error("Not enough %s to send" % ship.name)
                return FleetResult.NoAvailableShips
        self.browser.submit()


        # set target planet
        self.browser.select_form(name='details')
        self.browser["galaxy"] = coordinates.split(':')[0]
        self.browser["system"] = coordinates.split(':')[1]
        self.browser["position"] = coordinates.split(':')[2]
        self.browser.submit()

        # set mission and resouces to send
        self.browser.select_form(name='sendForm')
        self.browser.form.find_control('mission').readonly = False
        self.browser["mission"] = str(mission)
        self.browser["metal"] = str(resources.metal)
        self.browser["crystal"] = str(resources.crystal)
        self.browser["deuterium"] = str(resources.deuterium)
        self.browser.submit()
        self.logger.info("Sending %s %s from planet %s to coordinates %s" %
            (self.get_ships_list(ships), ("carrying %s" % resources) if resources != None else "", origin_planet.name, coordinates))
        return FleetResult.Success

    def get_ships_list(self, ships):
        return ", ".join([ str(ships.get(ship))  + ' ' + str(ship) for ship in ships])

    def get_tranport_fleet(self, resources):
        """Get fleet for transport"""
        resources_count = resources.total()
        ships_count = int(math.ceil(resources_count / 25000))
        return  { self.ships.get('lg') : ships_count}

    # def get_fleet_slots_usage(self):
    #     url = self.url_provider.get_page_url('fleet')
    #     res = self.browser.open(url)
    #     soup = BeautifulSoup(res.read())
    #     fleet_info_node = soup.findAll("div", {"class", "fleft"})
    #     slots_data = (next(node for node in fleet_info_node if "Frotas:" in node.text)).split(':')[1]
    #     current_slots = int(slots_data.split('/')[0])
    #     all_slots = int(slots_data.split('/')[1])
    #     return (current_slots, all_slots)

    def get_attack_fleet(self, target_planet):
        """Get fleet for attack"""
        resources = target_planet.resources.total()
        resources_count = resources * target_planet.loot
        ships_count = int(math.ceil(resources_count / 25000))
        return  { self.ships.get('lg') : ships_count}

class FleetResult(Enum):
    Success = 1
    WrongParameters = 2
    NoAvailableShips = 3
