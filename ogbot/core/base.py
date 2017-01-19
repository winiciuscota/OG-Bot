import logging


class BaseBot(object):
    """Base class for bot classes"""

    def __init__(self, browser, config, planets):
        # Authenticate and get browser instance
        self.browser = browser
        self.config = config

        # Get logger
        self.logger = logging.getLogger('OGBot')
        self.planets = planets

        # Set Default origin planet
        self.default_origin_planet = self.get_default_origin_planet(self.config.default_origin_planet_name)

        # self.planet will be None if the user doesn't specifies a valid planet name
        self.planet = self.get_player_planet_by_name(config.planet_name)

    # Util functions
    def get_player_planet_by_name(self, planet_name):
        """Get player planet by name. If there is no match returns None"""
        planets = self.planets
        if planet_name is None:
            return None

        planet = next(iter([planet for planet
                            in planets
                            if planet.name.lower() == planet_name.lower()]), None)
        return planet

    def get_default_origin_planet(self, planet_name):
        if planet_name is None:
            return self.planets[0]
        else:
            return self.get_player_planet_by_name(planet_name)

    @staticmethod
    def get_nearest_planet_to_coordinates(coordinates, planets):
        """Get the nearest planet to the target coordinates"""

        # Get the closest galaxy
        target_galaxy = int(coordinates.split(':')[0])
        planet_galaxies = set([int(planet.coordinates.split(':')[0]) for planet in planets])
        closest_galaxy = min(planet_galaxies, key=lambda x: abs(x - target_galaxy))

        # Get the closest system
        target_system = int(coordinates.split(':')[1])
        planet_systems = [int(planet.coordinates.split(':')[1])
                          for planet in planets
                          if planet.coordinates.split(':')[0] == str(closest_galaxy)]

        closest_system = min(planet_systems, key=lambda x: abs(x - target_system))

        planet = next((planet
                       for planet
                       in planets
                       if planet.coordinates.split(":")[0] == str(target_galaxy)
                       and planet.coordinates.split(":")[1] == str(closest_system)
                       ), None)

        if planet is None:
            raise EnvironmentError("Error getting closest planet from target")
        else:
            return planet
