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
    def auto_build_defenses(self):
        planets = get_planets()
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def get_defenses(self):
        planets = get_planets()
        for planet in planets:
            self.logger.info(self.defense_client.get_defenses(planet))

    def get_ships(self):
        planets = get_planets()
        for planet in planets:
            ships = self.hangar_client.get_ships(planet)
            self.logger.info("Displaying ships for planet %s:" % planet.name)
            for ship in ships:
                self.logger.info(ship)

    def get_planets(self):
        planets = self.general_client.get_planets()
        for planet in planets:
            self.logger.info(planet)

    def transport_resources_to_planet(self):
        planets = get_planets()
        target_planet = self.get_target_planet()
        self.logger.info("Main planet found: %s"  % target_planet)
        for planet in [planet for planet in planets if planet != target_planet]:
            resources = general.Resources(1000000, 1000000, 1000000)
            self.logger.info("Transporting %s from planet %s to planet %s" % (resources, planet.name, target_planet.name))
            self.fleet_client.transport_resources(planet, target_planet, resources)

    def auto_build_structure_to_planet(self):
        target_planet = self.get_target_planet()
        self.buildings_client.auto_build_structure(target_planet)

    # Util functions
    def get_planet(self):
        return self.planets

    def get_target_planet(self):
        planets = self.planets
        target_planet = [planet for planet in planets if planet.name.lower() == self.target_planet_name.lower()][0]
        return target_planet
