from base import BaseBot

from scraping import buildings, defense, general



class BuilderBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.defense_client = defense.Defense(browser, config)
        self.buildings_client = buildings.Buildings(browser, config)
        self.general_client = general.General(browser, config)

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

    def auto_build_structure_to_planet(self, planet):
        self.buildings_client.auto_build_structure(planet)

    def auto_build_structures(self):
        for planet in self.planets:
            self.buildings_client.auto_build_structure(planet)

    def get_weaker_planet(self):
        weaker_planet = self.buildings_client.get_weaker_planet()
        return weaker_planet

    def get_available_buildings_for_planet(self, planet):
        buildings = self.buildings_client.get_available_buildings_for_planet(planet)
        return buildings

    def auto_build_structure_to_weaker_planet(self):
        """
            Build the first available structure on the weaker planet
            If the planet has negative energy will prioritize energy buildings
        """

        weaker_planet = self.get_weaker_planet()
        resources = self.general_client.get_resources(weaker_planet)
        buildings = self.get_available_buildings_for_planet(weaker_planet)

        if len(buildings) > 0:
            building = buildings[0]
            if resources.energy < 0:
                energy_buildings = [building for building
                                                in buildings
                                                if building == building.BUILDINGS_DATA.get("sp")
                                                or building == building.BUILDINGS_DATA.get("fs") ]

                if len(energy_buildings) > 0:
                    building = energy_buildings[0]

            self.buildings_client.build_structure(building, weaker_planet)
        else:
            self.logger.info("No available buildings on planet %s" % weaker_planet)

