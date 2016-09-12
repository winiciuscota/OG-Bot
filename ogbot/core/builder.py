from base import BaseBot

from scraping import buildings, defense, general


class BuilderBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.defense_client = defense.Defense(browser, config)
        self.buildings_client = buildings.Buildings(browser, config)
        self.general_client = general.General(browser, config)
        self.planets = planets
        super(BuilderBot, self).__init__(browser, config, planets)

    def auto_build_defenses(self):
        """Auto build defenses on all planets"""
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses_to_planet(planet)

    def auto_build_defenses_to_planet(self):
        """
            Auto build defenses to planet
            :return: None
        """
        origin_planet = self.planet

        if origin_planet == None:
            self.logger.warning("Planet not found")
            return

        self.defense_client.auto_build_defenses_to_planet(origin_planet)

    def get_planet_for_construction(self):
        """
        Get the weaker planet that is not in construction mode
        :return: planet object
        """
        planets = self.planets
        planet = self.get_planet_candidate_for_construction(planets)
        return planet

    def get_planet_candidate_for_construction(self, planets=None):
        """
        Get the weaker planet that is not in construction mode
        :param planets: planets to search for, use all planets if None
        :return: planet object
        """

        if planets is None:
            planets = self.planets

        weaker_planet = self.buildings_client.get_weaker_planet(planets)
        construction_mode = self.buildings_client.is_in_construction_mode(weaker_planet)
        if construction_mode is False:
            return weaker_planet

        # If the weaker planets is in construction mode make a recursive call
        # looking for the weaker planet in the other planets
        planets = planets[:]
        planets.remove(weaker_planet)

        # If there is no more planets return None
        if not planets:
            return None

        return self.get_planet_candidate_for_construction(planets)

    def get_available_buildings_for_planet(self, planet):
        buildings = self.buildings_client.get_available_buildings_for_planet(planet)
        return buildings

    def auto_build_structures(self):
        """
            Auto build structures on all planets
        """

        for planet in self.planets:
            self.auto_build_structures_to_planet(planet)

    def auto_build_structures_to_planet(self, planet):
        """
            Build the first available structure on the weaker planet
            If the planet has negative energy will prioritize energy buildings
        """
        resources = self.general_client.get_resources(planet)
        available_buildings = self.get_available_buildings_for_planet(planet)

        if len(available_buildings) > 0:
            building = available_buildings[0]
            if resources.energy < 0:
                self.logger.info("Planet has not enough energy, building solar plant or fusion reactor")
                energy_buildings = [building for building
                                    in available_buildings
                                    if building.id == buildings.BUILDINGS_DATA.get("sp").id
                                    or building.id == buildings.BUILDINGS_DATA.get("fr").id]

                if len(energy_buildings) > 0:
                    # Get the last element from the list, this way the bot will build fusion reactors first
                    building = energy_buildings[-1]
                else:
                    self.logger.info("No available resources to buld solar plant or fusion reactor")

            self.buildings_client.build_structure(building, planet)
        else:
            self.logger.info("No available buildings on planet %s" % planet)
