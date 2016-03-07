from scraping import *
import logging
from datetime import timedelta
from datetime import datetime
import time
import random

class OgameBot:

    def __init__(self, config):
        #Authenticate and get browser instance
        auth_client = authentication.AuthenticationProvider(config)
        self.browser = auth_client.get_browser();
        self.config = config
        #Initialize scrapers
        self.general_client = general.General(self.browser, self.config)
        self.defense_client = defense.Defense(self.browser, self.config)
        self.hangar_client = hangar.Hangar(self.browser, self.config)
        self.fleet_client = fleet.Fleet(self.browser, self.config)
        self.galaxy_client = galaxy.Galaxy(self.browser, self.config)
        self.messages_client = messages.Messages(self.browser, self.config)
        self.movement_client = movement.Movement(self.browser, self.config)
        self.buildings_client = buildings.Buildings(self.browser, self.config)

        #Get logger
        self.logger = logging.getLogger('OGBot')
        self.planets = self.general_client.get_planets()

        #Set Default origin planet
        self.default_origin_planet = self.get_default_origin_planet(self.config.default_origin_planet_name)

        #self.planet will be None if the user doesn't species a valid planet name
        self.planet = self.get_player_planet_by_name(config.planet_name)

    # Bot functions
    def auto_build_defenses(self):
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def auto_build_defenses_to_planet(self):
        origin_planet = self.default_origin_planet
        self.defense_client.auto_build_defenses(origin_planet)

    def transport_resources_to_planet(self):
        """transport resources to the planet, if there is not planet especified the function will chose the default origin planet"""
        planets = self.planets

        if self.planet != None:
            destination_planet = self.planet
        else:
            self.logger.info("there is no specified target planet, using default origin planet instead")
            destination_planet = self.default_origin_planet

        self.logger.info("Destination planet found: %s"  % destination_planet)
        for planet in [planet for planet in planets if planet != destination_planet]:
            resources = general.Resources(20000000, 20000000, 20000000)
            self.fleet_client.transport_resources(planet, destination_planet, resources)

    def auto_build_structure_to_planet(self):
        origin_planet = self.default_origin_planet
        self.buildings_client.auto_build_structure(origin_planet)

    def auto_build_structures(self):
        for planet in self.planets:
            self.buildings_client.auto_build_structure(planet)

    def spy_nearest_planets(self, origin_planet = None, nr_range = 3):
        """Spy the nearest planets from origin"""

        if origin_planet == None:
            origin_planet = self.default_origin_planet

        self.logger.info("Getting nearest planets from %s", origin_planet.name)
        target_planets = self.get_nearest_planets(origin_planet, nr_range)

        for target_planet in target_planets:
            self.fleet_client.spy_planet(origin_planet, target_planet, self.config.spy_probes_count)

    def spy_nearest_inactive_planets(self, origin_planet = None, nr_range = 3):
        """ Spy the nearest inactive planets from origin"""

        if origin_planet == None:
            origin_planet = self.default_origin_planet

        self.logger.info("Spying nearest inactive planets from %s", origin_planet.name)

        target_planets = self.get_nearest_inactive_planets(origin_planet, nr_range)

        for target_planet in target_planets:
            self.fleet_client.spy_planet(origin_planet, target_planet, self.config.spy_probes_count)

    def auto_spy_inactive_planets(self, nr_range = None):

        if nr_range == None:
            nr_range = self.config.attack_range
        
        self.logger.info("Getting systems in range")
        systems = self.get_systems_in_range(nr_range, self.planet)
        self.logger.info("there is a total of %d systems in range" % len(systems))
        associated_systems = self.associate_systems(systems);

        for planet in self.planets:
            systems = [system[0] for system in associated_systems if system[1] == planet]
            self.logger.info("Getting inactive planets in range(%d) from %s" % (len(systems), planet.name))

            for system in systems:
                target_planets = self.get_inactive_planets_in_systems([system])

                for index, target_planet in enumerate(target_planets):
                    # delay before sending mission
                    if index > 1:
                         #Delay - wait a random time before sending fleet, this makes the bot less detectable
                        delay = random.randint(self.config.spy_fleet_min_delay, self.config.spy_fleet_max_delay)
                        self.logger.info("Waiting for %s seconds" % delay)
                        time.sleep(delay)

                    self.fleet_client.spy_planet(planet, target_planet, self.config.spy_probes_count)



    def associate_systems(self, systems):
        """Associate systems with the nearest planet"""

        associated_systems = []
        for system in systems:
            origin_planet = self.get_nearest_planet_to_coordinates(system + ":1")
            associated_systems.append((system, origin_planet))

        return associated_systems;

    def get_systems_in_range(self, nr_range, planet = None):
        """Return the systems in range"""

        systems = []
        if planet == None:
           planets = self.planets;
        else:
           planets = [planet]

        for p in self.planets:
            systems.append("%s:%s" % (p.coordinates.split(":")[0], p.coordinates.split(":")[1]))

            for i in range(1, nr_range + 1):
                previous_system = int(p.coordinates.split(":")[1]) + i
                later_system = int(p.coordinates.split(":")[1]) - i
                systems.append("%s:%s" % (p.coordinates.split(":")[0], str(previous_system)))
                systems.append("%s:%s" % (p.coordinates.split(":")[0], str(later_system)))
        
        # Return the list without duplicate systems
        return list(set(systems))


    def attack_inactive_planets_from_spy_reports(self):
        game_date = self.general_client.get_game_datetime()
        reports = self.get_spy_reports()
        
        # Stop if there is no fleet slot available
        slot_usage = self.movement_client.get_fleet_slots_usage()
        if slot_usage[0] >= slot_usage[1]:
            self.logger.warning("There is no fleet slot available")
            return True

        movements = [movement.destination_coords for movement
                                                 in self.movement_client.get_fleet_movement()]

        self.logger.info("Got %d reports" % len(reports))
        inactive_planets = [ report for report
                                    in set(reports)
                                    # Get reports from inactive players only
                                    if report.player_state == galaxy.PlayerState.Inactive
                                    # Get reports from last 2 minutes
                                    and report.report_datetime >= (game_date - timedelta(minutes=self.config.spy_report_life))
                                    # Dont attack planets that are already being attacked
                                    and report.coordinates not in movements]

        if len(inactive_planets) == 0:
            self.logger.info("There isn't any recent spy reports of inactive players")
            return False
        else:
            self.logger.info("Found %d recent spy reports of inactive players" % len(inactive_planets))

        distinct_inactive_planets = get_distinct_targets(inactive_planets)
        targets = sorted(distinct_inactive_planets, key=self.get_target_value, reverse=True)
        
        target = targets[0]
        origin_planet = self.get_nearest_planet_to_target(target)
        result = self.attack_inactive_planet(origin_planet, target)
        predicted_loot = 0
        if result == fleet.FleetResult.Success:
            predicted_loot += target.get_loot()
        slot_usage = self.movement_client.get_fleet_slots_usage()


        available_slots = slot_usage[1] - slot_usage[0]

        for target in targets[1:]:
            self.logger.info("Slot usage: %d/%d" % (slot_usage[1] - available_slots, slot_usage[1]))
            if available_slots > 0:
                if target.defenses == 0 and target.fleet == 0:
                    # Get the nearest planet from target
                    if self.planet == None:
                        origin_planet = self.get_nearest_planet_to_target(target)
                    else:
                        origin_planet = self.planet  

                    #Delay - wait a random time before sending fleet, this makes the bot less detectable
                    delay = random.randint(self.config.attack_fleet_min_delay, self.config.attack_fleet_max_delay)
                    self.logger.info("Waiting for %s seconds" % delay)
                    time.sleep(delay)

                    result = self.attack_inactive_planet(origin_planet, target)
                    if result == fleet.FleetResult.Success:
                        predicted_loot += target.get_loot()
                        available_slots -= 1
                elif target.defenses != 0:
                    self.logger.warning("target planet is defended (%s), maybe you should send some missiles first?" % target.defenses)
                elif target.fleet != 0:
                    self.logger.warning("target planet has fleet (%s)" % target.fleet)
            else:
                self.logger.warning("There is no fleet slot available")
                self.logger.info("Predicted loot is %s" % predicted_loot)
                return True
        self.logger.info("Predicted loot is %s" % predicted_loot)
        return True

    def auto_attack_inactive_planets(self):
        result = self.attack_inactive_planets_from_spy_reports()
        if result == False:
            self.logger.info("Sending Spy Probes")
            self.auto_spy_inactive_planets(self.config.attack_range)
            self.logger.info("Waiting %f seconds for probes to return" % self.config.time_to_wait_for_probes)
            time.sleep(self.config.time_to_wait_for_probes)
            self.attack_inactive_planets_from_spy_reports()
            self.clear_spy_reports()

    def auto_send_expeditions(self):
        for index, _ in enumerate(range(3)):

            if index > 1:
                #Delay - wait a random time before sending fleet, this makes the bot less detectable
                delay = random.randint(self.config.expedition_fleet_min_delay, self.config.expedition_fleet_max_delay)
                self.logger.info("Waiting for %s seconds" % delay)
                time.sleep(delay)

            target_planet = self.get_random_player_planet()
            res = self.send_expedition(target_planet)
            if res != fleet.FleetResult.Success:
                self.logger.warning("Error launching expedition, retrying...")
                #Retry 3 times
                for j in range(3):
                    target_planet = self.get_random_player_planet()
                    res = self.send_expedition(target_planet)
                    break

    def get_random_player_planet(self):
        return self.planets[random.randint(0, len(self.planets) - 1)]

    def send_expedition(self, target_planet):
        coordinates = self.get_expedition_coordinates(target_planet)
        res = self.fleet_client.send_expedition(target_planet, coordinates)
        return res           

    def get_expedition_coordinates(self, planet):
        galaxy = self.default_origin_planet.coordinates.split(':')[0]
        planet_system = self.default_origin_planet.coordinates.split(':')[1]
        system = str(int(planet_system) + random.randint(-self.config.expedition_range, self.config.expedition_range))

        coordinates = ":".join([galaxy, system, "16"])
        return coordinates       

    def attack_inactive_planet(self, origin_planet, target_planet):
        result = self.fleet_client.attack_inactive_planet(origin_planet, target_planet)
        return result
    
    def explore(self):
        self.auto_send_expeditions()
        self.auto_attack_inactive_planets()
        

    def clear_spy_reports(self):
        self.messages_client.clear_spy_reports()

    # Util functions
    def get_player_planet_by_name(self, planet_name):
        """Get player planet by name. If there is no match returns None"""
        planets = self.planets
        if planet_name == None:
            return None
            
        planet = next(iter([planet for planet
                                in planets
                                if planet.name.lower() == planet_name.lower()]), None)
        return planet

    def get_default_origin_planet(self, planet_name):
        if planet_name == None:
            return self.planets[0]
        else:
            return self.get_player_planet_by_name(planet_name)

    def get_planets_in_same_system(self):
        origin_planet = self.default_origin_planet
        planets = self.galaxy_client.get_planets(origin_planet.coordinates.split(':')[0],
                     origin_planet.coordinates.split(':')[1])
        return planets


    def get_planets_in_systems(self, systems):
        """Get planets in the given systems"""
        planets_in_systems = []
        for system_coordinates in systems:
            planets = self.galaxy_client.get_planets(system_coordinates.split(':')[0], system_coordinates.split(':')[1])
            planets_in_systems.extend(planets)
        return planets_in_systems

    def get_inactive_planets_in_systems(self, systems):
        """Get nearest inactive planets in the given systems"""

        planets = [planet for planet
                          in self.get_planets_in_systems(systems)
                          if planet.player_state == galaxy.PlayerState.Inactive
                          if planet.player_rank >= self.config.minimun_inactive_target_rank]
        return planets


    def get_nearest_planets(self, origin_planet = None, nr_range = 3):
        """Get nearest planets from origin planet"""

        if origin_planet == None:
            origin_planet = self.default_origin_planet
            
        self.logger.info("Getting nearest planets from %s", origin_planet.name)

        planets = []
        galaxy = origin_planet.coordinates.split(':')[0]
        system =  origin_planet.coordinates.split(':')[1]
        planets.extend(self.galaxy_client.get_planets(galaxy, system))
        for i in range(1, nr_range):
            target_previous_system = str(int(system) - i)
            target_later_system = str(int(system) + i)
            previous_planets = self.galaxy_client.get_planets(galaxy, target_previous_system)
            later_planets = self.galaxy_client.get_planets(galaxy, target_later_system)
            planets.extend(previous_planets)
            planets.extend(later_planets)
        return planets

    def get_nearest_inactive_planets(self, origin_planet = None, nr_range = 3):
        """Get nearest inactive planets from origin planet"""

        if origin_planet == None:
            origin_planet = self.default_origin_planet

        self.logger.info("Getting nearest inactive planets from %s", origin_planet.name)

        planets = [planet for planet
                          in self.get_nearest_planets(origin_planet, nr_range)
                          if planet.player_state == galaxy.PlayerState.Inactive
                          if planet.player_rank >= self.config.minimun_inactive_target_rank]
        return planets

    def get_spy_reports(self):
        """Get spy reports from the messages"""
        spy_reports = self.messages_client.get_spy_reports()
        return spy_reports

    def get_target_value(self, target):
        """Get the value of a target by its resources"""
        return target.resources.total() * target.loot

    def get_nearest_planet_to_target(self, target_planet):
        """Get the nearest planet to the target planet"""

        return self.get_nearest_planet_to_coordinates(target_planet.coordinates)

        

    def get_nearest_planet_to_coordinates(self, coordinates, planets = None):
        """Get the nearest planet to the target coordinates"""

        if planets == None:
            planets = self.planets

        planet_systems = [ int(planet.coordinates.split(':')[1]) for planet in planets ]
        target_system = int(coordinates.split(':')[1])
        closest_system = min(planet_systems, key = lambda x:abs(x - target_system))
        target_galaxy = coordinates.split(':')[0]
        planet = next((planet
                       for planet
                       in planets
                       if planet.coordinates.split(":")[0] == target_galaxy
                       and planet.coordinates.split(":")[1] == str(closest_system)
                       ), None)
        if planet == None:
            raise EnvironmentError("Error getting closest planet from target")
        else:
            return planet

    def log_index_page(self):
        """Log the index page"""
        self.general_client.log_index_page()

def get_distinct_targets(targets):
    """Given an list that possibly contains repeated targets, returns a list of distinct targets"""
    dict = {}
    for obj in targets:
        dict[obj.coordinates] = obj
    distinct_targets = dict.values()
    return distinct_targets

