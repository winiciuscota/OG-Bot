from __future__ import division
from bs4 import BeautifulSoup
import general
import math
from scraper import *


class Fleet(Scraper):
    def __init__(self, browser, config):
        super(Fleet, self).__init__(browser, config)

        self.general_client = general.General(browser, config)

    def spy_planet(self, origin_planet, destination_planet, spy_probes_count):

        self.logger.info("Spying planet %s (%s)", destination_planet.name, destination_planet.coordinates)

        result = self.send_fleet(origin_planet, destination_planet.coordinates,
                                 self.missions["spy"], {self.SHIPS_DATA.get('ep'): spy_probes_count})

        return result

    def send_expedition(self, origin_planet, coordinates):
        fleet = {
            # Small expedition fleet
            self.SHIPS_DATA.get('sg'): 1,
            self.SHIPS_DATA.get('lf'): 2,
            self.SHIPS_DATA.get('ep'): 1
        }

        self.logger.info("Sending expedition from planet %s to coordinates %s", origin_planet.name, coordinates)
        self.send_fleet(origin_planet, coordinates, self.missions.get("expedition"), fleet)

    def attack_inactive_planet(self, origin_planet, target_planet):
        fleet = self.get_attack_fleet(origin_planet, target_planet)

        self.logger.info("Attacking planet %s from planet %s", target_planet.planet_name, origin_planet.name)

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
        if resources is None:
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
            if not control.readonly:
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

        # set mission and resources to send
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
        if not resources.empty():
            self.logger.info("The fleet is transporting %s " % resources)

        return FleetResult.Success

    def get_fleet_slots_usage(self, mission=None, soup=None):
        """
            Get fleet slot usage data.
        """

        if soup is None:
            url = self.url_provider.get_page_url('fleet')
            res = self.open_url(url)
            soup = BeautifulSoup(res.read(), "lxml")

        slots_info = soup.find("div", {"id": "slots"})

        if slots_info is None:
            self.logger.warning("Error Getting fleet slots data")
            return 0, 15

        flefts = slots_info.findAll("div", {"class": "fleft"})

        if mission == self.missions.get("expedition"):
            node = flefts[1].findAll("span", {"class": "tooltip advice"})
        else:
            node = flefts[0].findAll("span", {"class": "tooltip advice"})

        slot_usage = "".join(node[0].findAll(text=True, recursive=False))

        try:
            result = (int(slot_usage.split('/')[0].strip()), int(slot_usage.split('/')[1].strip()))
        except ValueError:
            slot_usage = "".join(node[0].find("span", {"class": "overmark"}).findAll(text=True, recursive=False))
            result = (int(slot_usage.split('/')[0].strip()), int(slot_usage.split('/')[1].strip()))

        return result

    def get_tranport_fleet(self, resources, origin_planet=None):
        """
        Get fleet for transporting resources,
        Will use small cargos if there is enough of them.
        """

        resources_count = resources.total()

        return self.get_cargo_fleet_for_mission(origin_planet, resources_count)

    def get_attack_fleet(self, origin_planet, target_planet):
        """
        Get fleet for attacks to inactive targets.
        Will use small cargos if there is enough of them.
        :param origin_planet: Origin planet
        :param target_planet: Target planet
        :return: Optimized fleet for the mission
        """

        resources = target_planet.resources.total()
        resources_count = resources * target_planet.loot

        return self.get_cargo_fleet_for_mission(origin_planet, resources_count)

    def get_cargo_fleet_for_mission(self, origin_planet, resources_count):
        """
        :param origin_planet: Origin to check for cargos
        :param resources_count: Amount of resources to transport
        :return: Get fleet of cargos for the mission
        """
        small_cargos_count = self.get_ships_count(origin_planet, "sg")

        self.logger.info("Checking if there is enough small cargos for the mission")
        if (small_cargos_count * 5000) > resources_count:
            self.logger.info("Using small cargos")
            ships_count = int(math.ceil(resources_count / 5000))
            return {self.SHIPS_DATA.get('sg'): ships_count}
        else:
            self.logger.info("Not enough Small Cargos, using Large Cargos instead")
            ships_count = int(math.ceil(resources_count / 25000))
            large_cargos_count = self.get_ships_count(origin_planet, "lg")
            if ships_count > large_cargos_count:
                ships_count = large_cargos_count
            fleet = {self.SHIPS_DATA.get('lg'): ships_count}
            return fleet

    def get_ships_count(self, planet, ship_type):
        """
        :param planet: planet to get the count of ships
        :param ship_type: type of ships to count
        :return:
        """
        ships_count = [ship.amount for ship
                       in planet.ships
                       if ship.item.id == self.SHIPS_DATA.get(ship_type).id]

        return next(iter(ships_count), 0)


def get_ships_list(ships):
    return ", ".join([ships.get(ship).encode('utf-8') + ' ' + ship.name for ship in ships])
