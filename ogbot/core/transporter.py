from base import BaseBot
from scraping import fleet, general

class TransporterBot(BaseBot):
    """Logging functions for the bot"""
    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config)

        super(TransporterBot, self).__init__(browser, config, planets)

    def transport_resources_to_planet(self):
        """transport resources to the planet, if there is not planet especified the function will chose the default origin planet"""
        planets = self.planets

        if self.planet != None:
            destination_planet = self.planet
        else:
            self.logger.info("there is no specified target planet, using default origin planet instead")
            destination_planet = self.default_origin_planet

        self.logger.info("Destination planet found: %s"  % destination_planet)
        for planet in [planet for planet in planets if planet != destination_planet]:
            # todo use resources data within origin planet
            resources = general.Resources(20000000, 20000000, 20000000)
            self.fleet_client.transport_resources(planet, destination_planet, resources)
