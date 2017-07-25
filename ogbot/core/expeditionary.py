import random
import time

from base import BaseBot
from scraping import fleet


class ExpeditionaryBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config, planets)

        super(ExpeditionaryBot, self).__init__(browser, config, planets)

    def get_random_player_planet(self):
        return self.planets[random.randint(0, len(self.planets) - 1)]

    def send_expedition(self, target_planet):
        coordinates = self.get_expedition_coordinates(target_planet)
        res = self.fleet_client.send_expedition(target_planet, coordinates)
        return res

    def get_expedition_coordinates(self, planet):
        galaxy = planet.coordinates.split(':')[0]
        planet_system = planet.coordinates.split(':')[1]
        system = str(int(planet_system) + random.randint(-self.config.expedition_range, self.config.expedition_range))

        coordinates = ":".join([galaxy, system, "16"])
        return coordinates

    def auto_send_expeditions(self):
        for index, _ in enumerate(range(3)):

            if index > 1:
                # Delay - wait a random time before sending fleet, this makes the bot less detectable
                delay = random.randint(self.config.expedition_fleet_min_delay, self.config.expedition_fleet_max_delay)
                self.logger.info("Waiting for %s seconds" % delay)
                time.sleep(delay)

            target_planet = self.get_random_player_planet()
            res = self.send_expedition(target_planet)
            if res != fleet.FleetResult.Success:
                self.logger.warning("Error launching expedition, retrying...")
                # Retry 3 times
                for _ in range(3):
                    target_planet = self.get_random_player_planet()
                    res = self.send_expedition(target_planet)
                    break
