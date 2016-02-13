from scraping import *
import logging
from datetime import timedelta
from datetime import datetime
import time

class OgameBot:

    def __init__(self, username, password, universe, default_origin_planet_name, 
                    attack_range, time_to_wait_for_probes, spy_report_life, minimun_target_rank, planet_name):

        self.universe = universe

        #Authenticate and get browser instance
        self.browser = authentication.AuthenticationProvider(username, password, universe).get_browser();

        #Initialize scrapers
        self.general_client = general.General(self.browser, self.universe)
        self.defense_client = defense.Defense(self.browser, self.universe)
        self.hangar_client = hangar.Hangar(self.browser, self.universe)
        self.fleet_client = fleet.Fleet(self.browser, self.universe)
        self.galaxy_client = galaxy.Galaxy(self.browser, self.universe)
        self.messages_client = messages.Messages(self.browser, self.universe)
        self.movement_client = movement.Movement(self.browser, self.universe)
        self.buildings_client = buildings.Buildings(self.browser, self.universe)

        #Get logger
        self.logger = logging.getLogger('OGBot')
        self.planets = self.general_client.get_planets()
       
        #Set user variables
        self.default_origin_planet_name = default_origin_planet_name
        self.attack_range = int(attack_range)
        self.time_to_wait_for_probes = float(time_to_wait_for_probes)
        self.spy_report_life = int(spy_report_life)
        self.minimun_inactive_target_rank = int(minimun_target_rank)

        #Set Default origin planet
        self.default_origin_planet = self.get_default_origin_planet(default_origin_planet_name)
        self.planet = self.get_player_planet_by_name(planet_name)

    # Bot functions
    def auto_build_defenses(self):
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def auto_build_defenses_to_planet(self):
        origin_planet = self.default_origin_planet
        self.defense_client.auto_build_defenses(origin_planet)

    def transport_resources_to_planet(self):
        planets = self.planets
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

    def spy_nearest_planets(self, origin_planet = None, range = 3):
        """Spy the nearest planets from origin"""

        if origin_planet == None:
            origin_planet = self.default_origin_planet

        self.logger.info("Getting nearest planets from %s", origin_planet.name)
        target_planets = self.get_nearest_planets(origin_planet, range)

        for target_planet in target_planets:
            self.fleet_client.spy_planet(origin_planet, target_planet)

    def spy_nearest_inactive_planets(self, origin_planet = None, range = 3):
        """ Spy the nearest inactive planets from origin"""

        if origin_planet == None:
            origin_planet = self.default_origin_planet

        self.logger.info("Spying nearest inactive planets from %s", origin_planet.name)

        target_planets = self.get_nearest_inactive_planets(origin_planet, range)

        for target_planet in target_planets:
            self.fleet_client.spy_planet(origin_planet, target_planet)

    def auto_spy_inactive_planets(self, range = None):

        if range == None:
            range = self.attack_range

        if self.planet != None:
            self.spy_nearest_inactive_planets(self.planet, range)
        else:
            for origin_planet in self.planets:
                self.spy_nearest_inactive_planets(origin_planet, range)
        

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
                                    and report.report_datetime >= (game_date - timedelta(minutes=self.spy_report_life))
                                    # Dont attack planets that are already being attacked
                                    and report.coordinates not in movements]

        if len(inactive_planets) == 0:
            self.logger.info("There isn't any recent spy reports of inactive players")
            return False
        else:
            self.logger.info("Found %d recent spy reports of inactive players" % len(inactive_planets))

        distinct_inactive_planets = self.get_distinct_targets(inactive_planets)
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
            if available_slots > 0:
                if target.defenses == 0 and target.fleet == 0:
                    # Get the nearest planet from target
                    if self.planet == None:
                        origin_planet = self.get_nearest_planet_to_target(target)
                    else:
                        origin_planet = self.planet  
                    result = self.attack_inactive_planet(origin_planet, target)
                    if result == fleet.FleetResult.Success:
                        predicted_loot += target.get_loot()
                        available_slots = available_slots - 1
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
            self.auto_spy_inactive_planets(self.attack_range)
            self.logger.info("Waiting %f seconds for probes to return" % self.time_to_wait_for_probes)
            time.sleep(self.time_to_wait_for_probes)
            self.attack_inactive_planets_from_spy_reports()
            self.clear_inbox()

    def auto_send_expeditions(self):
        for i in range(3):
            self.logger.info("Launching %dth expedition" % i)
            self.fleet_client.send_expedition(self.default_origin_planet)

    def attack_inactive_planet(self, origin_planet, target_planet):
        result = self.fleet_client.attack_inactive_planet(origin_planet, target_planet)
        return result
    
    def explore(self):
        self.auto_send_expeditions()
        self.auto_attack_inactive_planets()
        

    def clear_inbox(self):
        self.messages_client.clear_inbox()

    # Util functions
    def get_player_planet_by_name(self, planet_name):
        planets = self.planets
        if planet_name == None:
            return None
            
        planet = [planet for planet
                                in planets
                                if planet.name.lower() == planet_name.lower()][0]
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
                          if planet.player_rank >= self.minimun_inactive_target_rank]
        return planets

    def get_spy_reports(self):
        """Get spy reports from the messages"""
        spy_reports = self.messages_client.get_spy_reports()
        return spy_reports

    def get_target_value(self, target):
        """Get the value of a target by its resources"""
        return target.resources.total() * target.loot

    def get_nearest_planet_to_target(self, target_planet, planets = None):
        """Get the nearest planet to the target planet"""

        if planets == None:
            planets = self.planets

        # Get planet systems
        planet_systems = [ int(planet.coordinates.split(':')[1]) for planet in planets ]
        target_system = int(target_planet.coordinates.split(':')[1])
        closest_system = min(planet_systems, key = lambda x:abs(x - target_system))
        target_galaxy = target_planet.coordinates.split(':')[0]
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

    def get_distinct_targets(self, targets):
        dict = {}
        for obj in targets:
            dict[obj.coordinates] = obj
        distinct_targets = dict.values()
        return distinct_targets

    def log_index_page(self):
        """Log the index page"""
        self.general_client.log_index_page()


