from authentication import AuthenticationProvider
import logging
import general
import defense
import buildings
import hangar
import fleet

class OgameBot:

    def __init__(self, username, password, universe, target_planet_name):
        self.universe = universe
        self.browser = AuthenticationProvider(username, password, universe).get_browser();
        self.general_client = general.General(self.browser, self.universe)
        self.defense_client = defense.Defense(self.browser, self.universe)
        self.hangar_client = hangar.Hangar(self.browser, self.universe)
        self.fleet_client = fleet.Fleet(self.browser, self.universe)
        self.buildings_client = buildings.Buildings(self.browser, self.universe)
        self.logger = logging.getLogger('ogame-bot')
        self.target_planet_name = target_planet_name
        self.planets = self.general_client.get_planets()

    # Bot functions

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

    def auto_build_defenses(self):
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def auto_build_defenses_to_planet(self):
        target_planet = self.get_target_planet()
        self.defense_client.auto_build_defenses(target_planet)

    def transport_resources_to_planet(self):
        planets = self.planets
        target_planet = self.get_target_planet()
        self.logger.info("Main planet found: %s"  % target_planet)
        for planet in [planet for planet in planets if planet != target_planet]:
            resources = general.Resources(1000000, 1000000, 0)
            self.fleet_client.transport_resources(planet, target_planet, resources)

    def auto_build_structure_to_planet(self):
        target_planet = self.get_target_planet()
        self.buildings_client.auto_build_structure(target_planet)

    def auto_build_structures(self):
        for planet in self.planets:
            self.buildings_client.auto_build_structure(planet)

    # Util functions
    def get_target_planet(self):
        planets = self.planets
        if self.target_planet_name == None:
            return planets[0]
        target_planet = [planet for planet in planets if planet.name.lower() == self.target_planet_name.lower()][0]
        return target_planet
