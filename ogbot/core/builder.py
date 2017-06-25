from base import BaseBot
from scraping import buildings, defense, general
import traceback


class BuilderBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.defense_client = defense.Defense(browser, config)
        self.buildings_client = buildings.Buildings(browser, config)
        self.general_client = general.General(browser, config)
        self.url_provider = self.general_client.url_provider
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
            try:
                self.force_repair_ships(planet)
                self.auto_build_structures_to_planet(planet)

            except Exception as e:
                exception_message = traceback.format_exc()
                self.logger.error(exception_message)

    def force_repair_ships(self, planet):
        self.collect_repaired_ships(planet)
        self.repair_ships(planet)

    def collect_repaired_ships(self, planet):
        if planet is not None:
            self.logger.info("Collecting ships on planet %s", planet)
            url = self.url_provider.get_page_url('collectShips', planet)
            self.general_client.open_url(url)

    def repair_ships(self, planet):
        if planet is not None:
            self.logger.info("Repairing ships on planet %s", planet)
            url = self.url_provider.get_page_url('repairShips', planet)
            self.general_client.open_url(url)

    def auto_build_structures_to_planet(self, planet):
        """
            Build the first available structure on the weaker planet
            If the planet has negative energy will prioritize energy buildings
        """
        if not planet.isMoon and (planet.spaceUsed >= self.config.maxFields \
           or (planet.spaceMax - planet.spaceUsed) <= self.config.minFreeFields):
            self.logger.warning("Too many buildings already on planet %s" % planet)
            return True

        available_buildings = self.get_available_buildings_for_planet(planet)
        building = None
        if not self.buildings_client.is_in_construction_mode():
            if available_buildings > 0:
                building = self.get_next_building_to_build_on_planet(
                            planet, available_buildings)

            if building:

                # Last built field gotta be lunar base for moons
                if planet.isMoon and (planet.spaceMax - planet.spaceUsed) <= 1 \
                    and building.id != 41:
                    self.logger.warning("Too many buildings already on moon %s" % planet)
                    return True

                self.buildings_client.build_structure(building, planet)
                self.sms_sender.send_sms("Building %s on planet %s" % (building, planet))
            else:
                self.logger.info("No available buildings on planet %s" % planet)
        else:
            self.logger.info("Planet is already in construction_mode: %s" % planet)

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

    def get_next_building_to_build_on_planet(self, planet, available_buildings):
        resources = self.general_client.get_resources(planet)
        priority_list = [
            41, #   LunarBase
            42, #   SensorPhalynx
            43, #   JumpGate
            15, #   NaniteFactory
            14, #   RobotFactory
            1,  #   MetalMine
            2,  #   KristalMine
            3,  #   DeuteriumSynthesizer
            21, #   Shipyard
            31, #   ResearchLab
            22, #   MetalStorage
            23, #   CrystalStorage
            24, #   DeuteriumStorage
        ]

        building = None
        if available_buildings:
            for abuilding in available_buildings:
                if abuilding.id in priority_list:
                    building = abuilding
                    break

            for building_candidate in available_buildings:
                if building_candidate.id in priority_list:
                    bc_priority = priority_list.index(building_candidate.id)
                    b_priority =  priority_list.index(building.id)
                    if bc_priority < b_priority:
                        building = building_candidate

                # If energy is below 0, it should be prioritized
                if resources.energy < 0:
                    # FusionReactor
                    if building_candidate.id == 12 and self.config.build_fusion_reactor:
                        building = building_candidate
                        break
                    # SolarPlant
                    elif building_candidate.id == 4:
                        building = building_candidate
                        break

        if building and resources.energy < -100:
            if not (building.id == 12 or building.id == 4):
                self.logger.info("Not much energy waiting to build a power plant")
                building = None

        if building:
            self.logger.info("%s selected for building" % building.name)

        return building
