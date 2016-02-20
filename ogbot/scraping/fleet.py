from __future__ import division
import util
from mechanize import Browser
import mechanize
from bs4 import BeautifulSoup
import re
import logging
import urlparse
import general
import math
from scraper import *

class Fleet(Scraper):
    def __init__(self, browser, universe):
        super(Fleet, self).__init__(browser, universe)

        self.general_client = general.General(browser, universe)


    def spy_planet(self, origin_planet, destination_planet):
        spy_probes_count = 5

        self.send_fleet(origin_planet, destination_planet.coordinates,
            self.missions["spy"], { self.ships.get('ep') : spy_probes_count})


    def send_expedition(self, origin_planet, coordinates):
        fleet = { 
            self.ships.get('sg') : 1,
            self.ships.get('lf') : 2,
            self.ships.get('ep') : 1
            }

        

        self.logger.info("Sending expedition from planet %s to coordinates %s", origin_planet.name, coordinates)

        self.send_fleet(origin_planet, coordinates, self.missions.get("expedition"), fleet)


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

        self.send_fleet(origin_planet, destination_planet.coordinates,
             self.missions["transport"], fleet, resources)

    def send_fleet(self, origin_planet, coordinates, mission, ships, resources=None):
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
        resp = self.open_url(url)

        try:
            self.browser.select_form(name='shipsChosen')
        except mechanize.FormNotFoundError:
            self.logger.error('The planet has no available ships')
            return FleetResult.NoAvailableShips

        # set ships to send
        soup = BeautifulSoup(resp.read(), "lxml")
        for ship, amount in ships.iteritems():
            self.logger.info("Adding %d %s to the mission fleet" % (amount, ship.name))
            control_name = "am" + str(ship.id)
            control = self.browser.form.find_control(control_name)
            # If there is no available ships exit
            if control.readonly == False:
                self.browser[control_name] = str(amount)
            else:
                self.logger.warning("Not enough %s to send" % ship.name)
                return FleetResult.NoAvailableShips
        self.submit_request()

        # set target planet
        self.browser.select_form(name='details')
        self.browser["galaxy"] = coordinates.split(':')[0]
        self.browser["system"] = coordinates.split(':')[1]
        self.browser["position"] = coordinates.split(':')[2]
        self.submit_request()

        # set mission and resouces to send
        self.browser.select_form(name='sendForm')
        self.browser.form.find_control('mission').readonly = False
        self.browser["mission"] = str(mission)
        self.browser["metal"] = str(resources.metal)
        self.browser["crystal"] = str(resources.crystal)
        self.browser["deuterium"] = str(resources.deuterium)
        self.submit_request()
        self.logger.info("Sending %s from planet %s to coordinates %s" % (
            self.get_ships_list(ships), origin_planet.name, coordinates))
        if resources.empty() != True:
            self.logger.info("The fleet is transporting %s " % resources)

        return FleetResult.Success

    def get_ships_list(self, ships):
        return ", ".join([ str(ships.get(ship)) + ' ' + ship.name for ship in ships])

    def get_tranport_fleet(self, resources):
        """Get fleet for transport"""
        resources_count = resources.total()
        ships_count = int(math.ceil(resources_count / 25000))
        return  { self.ships.get('lg') : ships_count}

    def get_fleet_slots_usage(self):
        raise NotImplementedError("Use the get get_fleet_slots_usage function from movement")
        url = self.url_provider.get_page_url('fleet')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        fleet_info_node = soup.findAll("div", {"class", "fleft"})
        slots_data = (next(node for node in fleet_info_node if "Frotas:" in node.text)).split(':')[1]
        current_slots = int(slots_data.split('/')[0])
        all_slots = int(slots_data.split('/')[1])
        return (current_slots, all_slots)

    def get_attack_fleet(self, target_planet):
        """Get fleet for attack"""
        resources = target_planet.resources.total()
        resources_count = resources * target_planet.loot
        ships_count = int(math.ceil(resources_count / 25000))
        return  { self.ships.get('lg') : ships_count}


