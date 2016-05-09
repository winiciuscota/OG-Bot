from base import BaseBot

from scraping import buildings, defense



class BuilderBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.defense_client = defense.Defense(browser, config)
        self.buildings_client = buildings.Buildings(browser, config)

        super(BuilderBot, self).__init__(browser, config, planets)

    def auto_build_defenses(self):
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def auto_build_defenses_to_planet(self):
        origin_planet = self.planet

        if origin_planet == None:
            self.logger.warning("Planet not found")
            return

        self.defense_client.auto_build_defenses(origin_planet)

    def auto_build_structure_to_planet(self):
        origin_planet = self.planet

        if origin_planet == None:
            self.logger.warning("Planet not found")
            return

        self.buildings_client.auto_build_structure(origin_planet)

    def auto_build_structures(self):
        for planet in self.planets:
            self.buildings_client.auto_build_structure(planet)

    def get_weaker_planet(self):
        weaker_planet = self.buildings_client.get_weaker_planet()
        return weaker_planet
