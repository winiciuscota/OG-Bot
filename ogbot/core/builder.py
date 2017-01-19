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

    def get_planet_for_construction(self):
        return self.get_candidate_planet_for_construction(self.planets)

    def get_candidate_planet_for_construction(self, planets=None):
        """
        Get the least developed planet that is not in construction mode
        :param planets: planets to search for, use all planets if None
        :return: planet object
        """

        least_developed_planet = self.get_least_developed_planet()

        construction_mode = self.buildings_client.is_in_construction_mode(least_developed_planet)
        if construction_mode is False:
            return least_developed_planet

        # If the least developed planet is in construction mode make a recursive call
        # looking for the second least developed planet
        planets = planets[:]
        planets.remove(least_developed_planet)

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
        available_buildings = self.filter_available_buildings(available_buildings, self.config)

        if len(available_buildings) > 0:
            building = available_buildings[0]
            if resources.energy < 0:
                self.logger.info("Planet has not enough energy, building solar plant or fusion reactor")

                id_energy_buildings = [buildings.BUILDINGS_DATA.get("sp").id,
                                       buildings.BUILDINGS_DATA.get("fr").id]

                energy_buildings = filter(lambda value: value.id in id_energy_buildings, available_buildings)

                if len(energy_buildings) > 0:
                    # Get the last element from the list, this way the bot will build fusion reactors first
                    building = energy_buildings[-1]
                else:
                    self.logger.info("No available resources to build solar plant or fusion reactor")

            self.buildings_client.build_structure(building, planet)
        else:
            self.logger.info("No available buildings on planet %s" % planet)

    def get_least_developed_planet(self):
        return min(self.planets, key=self.get_planet_building_total_lvl)

    def get_planet_building_total_lvl(self, planet):
        planet_buildings = self.buildings_client.get_buildings(planet)
        ignored_buildings = self.get_ignored_buildings(self.config)
        filtered_planet_buildings = filter(lambda x: x.item.id not in ignored_buildings, planet_buildings)
        return sum(x.amount for x in filtered_planet_buildings)

    def get_ignored_buildings(self, config):
        excluded_buildings = []

        if not config.build_solar_plant:
            self.logger.info("Ignoring solar plant")
            excluded_buildings.append(buildings.BUILDINGS_DATA.get("sp").id)

        if not config.build_fusion_reactor:
            self.logger.info("Ignoring fusion reactor")
            excluded_buildings.append(buildings.BUILDINGS_DATA.get("fr").id)

        if not config.build_storage:
            self.logger.info("Ignoring storage buildings")
            excluded_buildings.append(buildings.BUILDINGS_DATA.get("ms").id)
            excluded_buildings.append(buildings.BUILDINGS_DATA.get("cs").id)
            excluded_buildings.append(buildings.BUILDINGS_DATA.get("dt").id)

        return excluded_buildings

    def filter_available_buildings(self, available_buildings):
        """
        :param available_buildings: list of buildings
        :return: filtered list of available buildings
        """

        ignored_buildings = self.get_ignored_buildings(self.config)
        available_buildings = filter(lambda building: building.id not in ignored_buildings, available_buildings)

        return available_buildings
