from base import BaseBot
from scraping import fleet, general, hangar
from copy import copy


class TransporterBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config)
        self.hangar_client = hangar.Hangar(browser, config)
        self.general_client = general.General(browser, config)

        super(TransporterBot, self).__init__(browser, config, planets)

    def transport_resources_to_planet(self, planet=None):
        """transport resources to the planet,
        if there is not planet especified the function will chose the default origin planet
        """
        planets = self.planets

        if self.planet is not None:
            destination_planet = self.planet
        elif planet is not None:
            destination_planet = planet
        else:
            self.logger.info("there is no specified target planet, using default origin planet instead")
            destination_planet = self.default_origin_planet

        self.logger.info("Transporting resources to planet: %s" % destination_planet.name)
        for planet in [planet for planet in planets if planet != destination_planet]:
            planet.ships = self.hangar_client.get_ships(planet)
            resources = self.general_client.get_resources(planet)
            restricted_resources = self.get_restrict_resources_under_user_preferences(resources)
            self.fleet_client.transport_resources(planet, destination_planet, restricted_resources)

    def get_restrict_resources_under_user_preferences(self, resources):
        restricted_resources = copy(resources)

        restricted_resources.energy = 0

        if not self.config.transport_metal:
            restricted_resources.metal = 0

        if not self.config.transport_crystal:
            restricted_resources.crystal = 0

        if not self.config.transport_deuterium:
            restricted_resources.deuterium = 0

        return restricted_resources
