from __future__ import division
from bs4 import BeautifulSoup
import general
import math
from scraper import *
from core.base import BaseBot
import hangar


class Fleet(Scraper):
    def __init__(self, browser, config, planets):
        super(Fleet, self).__init__(browser, config)

        self.general_client = general.General(browser, config)
        self.planets = planets
        self.hangar_client = hangar.Hangar(browser, config)

    def spy_planet_from(self, origin_planet, destination_planet, spy_probes_count):

        self.logger.info("Spying planet %s (%s)", destination_planet.name, destination_planet.coordinates)

        result = self.send_fleet(origin_planet, destination_planet.coordinates,
                                 self.missions["spy"], {self.SHIPS_DATA.get('ep'): spy_probes_count})

        return result

    def spy_planet(self, destination_planet, spy_probes_count):

        # Get the nearest planets from target
        nearest_planets = BaseBot.get_nearest_planets_to_target(destination_planet, self.planets)

        # Spy from each planet ordered by proximity until success or error
        for planet in nearest_planets:
            result = self.spy_planet_from(planet, destination_planet, spy_probes_count)

            # Stop on success or no more slots
            if result == FleetResult.Success or result == FleetResult.NoAvailableSlots:
                break

        return result

    def send_expedition(self, origin_planet, coordinates):
        fleet = {
            # Small expedition fleet
            self.SHIPS_DATA.get('sg'): 1,
            self.SHIPS_DATA.get('lf'): 2,
            self.SHIPS_DATA.get('ep'): 1
        }

        self.logger.info("Sending expedition from planet %s to coordinates %s", origin_planet.coordinates, coordinates)
        self.send_fleet(origin_planet, coordinates, self.missions.get("expedition"), fleet)

    def attack_inactive_planet(self, origin_planet, target_planet):
        fleet = self.get_attack_fleet(origin_planet, target_planet)

        self.logger.info("Attacking planet %s from planet %s", target_planet.coordinates, origin_planet.coordinates)

        result = self.send_fleet(origin_planet, target_planet.coordinates,
                                 self.missions["attack"], fleet)
        return result

    def fleet_escape(self, target):
        resources = self.general_client.get_resources(target)
        ships = self.hangar_client.get_ships(target)

        ss = self.SHIPS_DATA.get('ss')
        lf = self.SHIPS_DATA.get('lf')

        fleet = {ship.item: ship.amount
                 for ship in ships
                 if ship.amount > 0
                 # Ignore solar satellites
                 and not ship.item.id == ss.id
                 # Allow moon fleet destruction
                 and not (ship.item.id == lf.id
                    and ship.amount > 1500)}

        if len(fleet) == 0:
            self.logger.warning('No fleet available, aborting escape')
            return True

        safe_planets = [planet for planet in self.planets
                        if planet.coordinates != target.coordinates
                        and planet.safe]

        nearest = BaseBot.get_nearest_planet_to_target(target, safe_planets)

        self.send_fleet(target, nearest.coordinates,
                        self.missions["transfer"], fleet, resources)

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

        ss = self.SHIPS_DATA.get('ss')
        sent = 0

        # set ships to send
        for ship, amount in ships.iteritems():

            # Ignore ships with 0 amount and solar satellites
            if amount <= 0 or ship.id == ss.id:
                continue

            self.logger.info("Adding %d %s to the mission fleet" % (amount, ship.name))
            control_name = "am" + str(ship.id)
            control = self.browser.form.find_control(control_name)

            # If there is no available ships exit
            if not control.readonly:
                self.browser[control_name] = str(amount)

            else:
                self.logger.warning("Not enough %s to send" % ship.name)
                return FleetResult.NoAvailableShips

            sent = sent + amount

        if sent <= 0:
            self.logger.error('The planet has no available ships')
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

    def get_attack_loot(self, origin_planet, target_planet):
        """
        Get loot for attacks to inactive targets.
        :param origin_planet: Origin planet
        :param target_planet: Target planet
        :return: Predicted loot
        """

        resources = target_planet.resources.total()
        resources_count = resources * target_planet.loot

        fleet = self.get_attack_fleet(origin_planet, target_planet)

        maxLoot = 0

        for ship, amount in fleet.iteritems():
            maxLoot += self.SHIPS_SIZE.get(str(ship.id)) * amount

        if resources_count >= maxLoot:
            return maxLoot

        return resources_count


    def get_cargo_fleet_for_mission(self, origin_planet, resources_count):
        """
        :param origin_planet: Origin to check for cargos
        :param resources_count: Amount of resources to transport
        :return: Get fleet of cargos for the mission
        """

        small_cargos_count = self.get_ships_count(origin_planet, "sg")
        large_cargos_count = self.get_ships_count(origin_planet, "lg")
        recyclers_count = self.get_ships_count(origin_planet, "r")

        # self.logger.info("Computing small cargos / recyclers / large cargos for the mission")
        # self.logger.info("Resources : %d" % resources_count)

        # self.logger.info("Available small cargos : %d" % small_cargos_count)
        # self.logger.info("Available large cargos : %d " % large_cargos_count)
        # self.logger.info("Available recyclers : %d " % recyclers_count)

        sel_lg_count, left_count = update_count(large_cargos_count, resources_count, 25000, False)
        sel_recycler_count, left_count = update_count(recyclers_count, left_count, 20000, False)
        sel_sg_count, left_count = update_count(small_cargos_count, left_count, 5000, True)


        fleet = {}

        if sel_sg_count:
            #self.logger.info("Small cargos : %d " % sel_sg_count)
            fleet[ self.SHIPS_DATA.get('sg') ] = sel_sg_count

        if sel_lg_count:
            #self.logger.info("Large cargos : %d " % sel_lg_count)
            fleet[ self.SHIPS_DATA.get('lg') ] = sel_lg_count

        if sel_recycler_count:
            #self.logger.info("Recyclers : %d " % sel_recycler_count)
            fleet[ self.SHIPS_DATA.get('r') ] = sel_recycler_count

        if len(fleet) == 0:
            fleet[ self.SHIPS_DATA.get('lg') ] = 0

        #self.logger.info("Leftover resources : %d" % left_count)

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
    return ", ".join([str(ships.get(ship)) + ' ' + ship.name for ship in ships])


def update_count(sel_count, res_count, sel_size, getCeil):
    if sel_count == 0:
        return 0, res_count

    count = float(res_count) / sel_size
    count = math.ceil(count) if getCeil \
            else math.floor(count)
    count = int(count)

    if count > sel_count:
        count = sel_count

    left = res_count - count * sel_size

    if left < 0:
        left = 0

    return count, left

