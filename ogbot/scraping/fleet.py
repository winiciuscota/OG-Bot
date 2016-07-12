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
import time
import random

class Fleet(Scraper):
    def __init__(self, browser, config):
        super(Fleet, self).__init__(browser, config)

        self.general_client = general.General(browser, config)

    def spy_planet(self, origin_planet, destination_planet, spy_probes_count):

        self.logger.info("Spying planet %s (%s)", destination_planet.name, destination_planet.coordinates)

        result = self.send_fleet(origin_planet, destination_planet.coordinates,
            self.missions["spy"], { self.SHIPS_DATA.get('ep') : spy_probes_count})

        return result

    def send_expedition(self, origin_planet, coordinates):
        fleet = {
            # Small expeditino fleet
            self.SHIPS_DATA.get('sg') : 1,
            self.SHIPS_DATA.get('lf') : 2,
            self.SHIPS_DATA.get('ep') : 1
            }

        self.logger.info("Sending expedition from planet %s to coordinates %s", origin_planet.name, coordinates)
        self.send_fleet(origin_planet, coordinates, self.missions.get("expedition"), fleet)

    def attack_inactive_planet(self, origin_planet, target_planet):
        fleet = self.get_attack_fleet(origin_planet, target_planet)

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

        fleet = self.get_tranport_fleet(resources, origin_planet)

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

        soup = BeautifulSoup(resp.read(), "lxml")
        fleet_slots = self.get_fleet_slots_usage(mission, soup)

        if fleet_slots[0] >= fleet_slots[1]:
            self.logger.error('No available slots')
            return FleetResult.NoAvailableSlots

        try:
            self.browser.select_form(name='shipsChosen')
        except mechanize.FormNotFoundError:
            self.logger.error('The planet has no available ships')
            return FleetResult.NoAvailableShips

        # set ships to send
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
        try:
            self.browser.select_form(name='details')
        except mechanize.FormNotFoundError:
            self.logger.error('Error sending ships')
            return FleetResult.NoAvailableShips
        self.browser["galaxy"] = coordinates.split(':')[0]
        self.browser["system"] = coordinates.split(':')[1]
        self.browser["position"] = coordinates.split(':')[2]
        self.submit_request()

        # set mission and resouces to send
        try:
            self.browser.select_form(name='sendForm')
        except mechanize.FormNotFoundError:
            self.logger.error('Error sending ships')
            return FleetResult.NoAvailableShips
        self.browser.form.find_control('mission').readonly = False
        self.browser["mission"] = str(mission)
        self.browser["metal"] = str(resources.metal)
        self.browser["crystal"] = str(resources.crystal)
        self.browser["deuterium"] = str(resources.deuterium)
        self.submit_request()
        self.logger.info("Sending %s from planet %s to coordinates %s" % (
            get_ships_list(ships), origin_planet.name, coordinates))
        if resources.empty() != True:
            self.logger.info("The fleet is transporting %s " % resources)

        return FleetResult.Success

    def get_fleet_slots_usage(self, mission = None, soup = None):
        """
            Get fleet slot usage data.
        """

        if soup == None:
            url = self.url_provider.get_page_url('fleet')
            res = self.open_url(url)
            soup = BeautifulSoup(res.read(), "lxml")

        slots_info = soup.find("div", {"id": "slots"})
        flefts = slots_info.findAll("div", {"class": "fleft"})

        if mission == self.missions.get("expedition"):
            node = flefts[1].findAll("span", {"class": "tooltip advice"})
        else:
            node = flefts[0].findAll("span", {"class": "tooltip advice"})

        slot_usage = "".join(node[0].findAll(text=True, recursive=False))

        try:
            result = (int(slot_usage.split('/')[0].strip()), int(slot_usage.split('/')[1].strip()))
        except ValueError:
            slot_usage = "".join(node[0].find("span", {"class" : "overmark"}).findAll(text=True, recursive=False))
            result = (int(slot_usage.split('/')[0].strip()), int(slot_usage.split('/')[1].strip()))

        return result

    def get_tranport_fleet(self, resources, origin_planet = None):
        """
            Get fleet for transporting resources,
            Will use small cargos if there is enough of them.
        """

        resources_count = resources.total()

        if origin_planet != None:
            small_cargos = self.get_small_cargos(origin_planet)
            self.logger.info("Checking if there is enough small cargos for the mission")
            if (small_cargos.amount * 5000) > (resources_count):
                self.logger.info("Using small cargos")
                ships_count = int(math.ceil(resources_count / 5000))
                return {self.SHIPS_DATA.get('sg'): ships_count}

        self.logger.info("Not enough Small Cargos, using Large Cargos instead")
        ships_count = int(math.ceil(resources_count / 25000))
        fleet = {self.SHIPS_DATA.get('lg'): ships_count}
        return fleet

    def get_attack_fleet(self, origin_planet, target_planet):
        """
            Get fleet for attacks to inactive targets.
            Will use small cargos if there is enough of them.
        """

        resources = target_planet.resources.total()
        resources_count = resources * target_planet.loot

        small_cargos = self.get_small_cargos(origin_planet)
        self.logger.info("Checking if there is enough small cargos for the mission")
        if (small_cargos.amount * 5000) > (resources_count):

            self.logger.info("Using small cargos")
            ships_count = int(math.ceil(resources_count / 5000))
            return {self.SHIPS_DATA.get('sg'): ships_count}

        self.logger.info("Not enough Small Cargos for this target, using Large Cargos instead")
        ships_count = int(math.ceil(resources_count / 25000))
        return  { self.SHIPS_DATA.get('lg') : ships_count}


    def get_small_cargos(self, origin_planet):
        small_cargos_aux = [item_order for item_order
                            in origin_planet.ships
                            if item_order.item.id == self.SHIPS_DATA.get("sg").id]

        small_cargos = next(iter(small_cargos_aux), None)

        return small_cargos

def get_ships_list(ships):
    return ", ".join([ str(ships.get(ship)) + ' ' + ship.name for ship in ships])
