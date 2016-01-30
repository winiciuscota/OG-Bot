from scraping import *
import logging
from datetime import timedelta
from datetime import datetime
import time

class OgameBot:

    def __init__(self, username, password, universe, default_origin_planet_name, 
                    attack_range, time_to_wait_for_probes, spy_report_life):
        self.universe = universe
        self.browser = authentication.AuthenticationProvider(username, password, universe).get_browser();
        self.general_client = general.General(self.browser, self.universe)
        self.defense_client = defense.Defense(self.browser, self.universe)
        self.hangar_client = hangar.Hangar(self.browser, self.universe)
        self.fleet_client = fleet.Fleet(self.browser, self.universe)
        self.buildings_client = buildings.Buildings(self.browser, self.universe)
        self.logger = logging.getLogger('ogame-bot')
        self.default_origin_planet_name = default_origin_planet_name
        self.planets = self.general_client.get_planets()
        self.default_origin_planet = self.get_origin_planet()
        self.galaxy_client = galaxy.Galaxy(self.browser, self.universe)
        self.messages_client = messages.Messages(self.browser, self.universe)
        self.movement_client = movement.Movement(self.browser, self.universe)
        self.attack_range = int(attack_range)
        self.time_to_wait_for_probes = float(time_to_wait_for_probes)
        self.spy_report_life = int(spy_report_life)

    # Bot functions
    def auto_build_defenses(self):
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def auto_build_defenses_to_planet(self):
        origin_planet = self.get_origin_planet()
        self.defense_client.auto_build_defenses(origin_planet)

    def transport_resources_to_planet(self):
        planets = self.planets
        destination_planet = self.get_origin_planet()
        self.logger.info("Destination planet found: %s"  % destination_planet)
        for planet in [planet for planet in planets if planet != destination_planet]:
            resources = general.Resources(10000000, 10000000, 10000000)
            self.fleet_client.transport_resources(planet, destination_planet, resources)

    def auto_build_structure_to_planet(self):
        origin_planet = self.get_origin_planet()
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

    def auto_spy_inactive_planets(self, range = 3):
        target_planets = []
        
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

        targets = sorted(inactive_planets, key=self.get_target_value, reverse=True)
            
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
                if target.defenses == 0:
                    # Get the nearest planet from target
                    origin_planet = self.get_nearest_planet_to_target(target)
                    result = self.attack_inactive_planet(origin_planet, target)
                    if result == fleet.FleetResult.Success:
                        predicted_loot += target.get_loot()
                        available_slots = available_slots - 1
                else:
                    self.logger.warning("target planet is defended")
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


    def attack_inactive_planet(self, origin_planet, target_planet):
        result = self.fleet_client.attack_inactive_planet(origin_planet, target_planet)
        return result
        
    def clear_inbox(self):
        self.messages_client.clear_inbox()

    # Logging functions
    def log_planets(self):
        planets = self.planets
        self.logger.info("Logging planets")
        for planet in planets:
            self.logger.info(planet)

    def log_defenses(self):
        planets = self.planets
        self.logger.info("Logging defenses")
        for planet in planets:
            self.logger.info(self.defense_client.get_defenses(planet))

    def log_ships(self):
        planets = self.planets
        for planet in planets:
            ships = self.hangar_client.get_ships(planet)
            self.logger.info("Logging ships for planet %s:" % planet.name)
            for ship in ships:
                self.logger.info(ship)

    def log_overview(self):
        results = []
        for planet in self.planets:
            resources = self.general_client.get_resources(planet)
            results.append((planet, resources))
        for res in results:
            self.logger.info("Planet %s:", res[0])
            self.logger.info("Resources: [%s]", res[1])

    def log_planets_in_same_system(self):
        planets = self.get_planets_in_same_ss()
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_planets(self):
        planets = self.get_nearest_planets(nr_range =  15)
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_inactive_planets(self):
        planets = self.get_nearest_inactive_planets(nr_range = 15)
        for planet in planets:
            self.logger.info(planet)

    def log_spy_reports(self):
        spy_reports = self.get_spy_reports()
        for spy_report in spy_reports:
            self.logger.info("Date:%s - %s" % (spy_report.report_datetime, spy_report))

    def log_game_datetime(self):
        time = self.general_client.get_game_datetime()
        self.logger.info(datetime)

    def log_fleet_movement(self):
        movements = self.movement_client.get_fleet_movement()
        for movement in movements:
            self.logger.info(movement)

    # Util functions
    def get_origin_planet(self):
        planets = self.planets
        if self.default_origin_planet_name == None:
            return planets[0]
            
        origin_planet = [planet for planet
                                in planets
                                if planet.name.lower() == self.default_origin_planet_name.lower()][0]
        return origin_planet

    def get_planets_in_same_system(self):
        origin_planet = self.get_origin_planet()
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
                          if planet.player_state == galaxy.PlayerState.Inactive]
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

    def log_index_page(self):
        """Log the index page"""
        self.general_client.log_index_page()
