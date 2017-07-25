from base import BaseBot
from scraping import galaxy, fleet
from random import shuffle
import random, time, traceback
import movement


class SpyBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config, planets)
        self.galaxy_client = galaxy.Galaxy(browser, config)
        self.movement_bot = movement.MovementBot(browser, config, planets)

        super(SpyBot, self).__init__(browser, config, planets)

    def get_planets_in_systems(self, systems):
        """Get planets in the given systems"""
        planets_in_systems = []
        for system_coordinates in systems:
            planets = self.galaxy_client.get_planets(system_coordinates.split(':')[0], system_coordinates.split(':')[1])
            planets_in_systems.extend(planets)
        return planets_in_systems

    def get_inactive_planets_in_systems(self, systems):
        """Get nearest inactive planets in the given systems"""

        # debug
        # print 'Min rank :', self.config.minimum_inactive_target_rank
        # print 'Max rank :', self.config.maximum_inactive_target_rank

        # for planet in self.get_planets_in_systems(systems):
            
        #     print planet.player_state
        #     print galaxy.PlayerState.Inactive
        #     print planet.player_rank

        #     if planet.player_state == galaxy.PlayerState.Inactive \
        #     and planet.player_rank >= self.config.minimum_inactive_target_rank \
        #     and planet.player_rank <= self.config.maximum_inactive_target_rank:
        #         print 'Valid  target'

        #     else:
        #       print 'Invalid target'

        planets = [planet for planet
                   in self.get_planets_in_systems(systems)
                   if planet.player_state == galaxy.PlayerState.Inactive
                   and planet.player_rank >= self.config.minimum_inactive_target_rank
                   and planet.player_rank <= self.config.maximum_inactive_target_rank]
        return planets

    def get_nearest_planets(self, origin_planet=None, nr_range=3):
        """Get nearest planets from origin planet"""

        if origin_planet is None:
            origin_planet = self.default_origin_planet

        self.logger.info("Getting nearest planets from %s", origin_planet.name)

        planets = []
        galaxy = origin_planet.coordinates.split(':')[0]
        system = origin_planet.coordinates.split(':')[1]
        planets.extend(self.galaxy_client.get_planets(galaxy, system))
        for i in range(1, nr_range):
            target_previous_system = str(int(system) - i)
            target_later_system = str(int(system) + i)
            previous_planets = self.galaxy_client.get_planets(galaxy, target_previous_system)
            later_planets = self.galaxy_client.get_planets(galaxy, target_later_system)
            planets.extend(previous_planets)
            planets.extend(later_planets)
        return planets

    def get_nearest_inactive_planets(self, origin_planet=None, nr_range=3):
        """Get nearest inactive planets from origin planet"""

        if origin_planet is None:
            origin_planet = self.default_origin_planet

        self.logger.info("Getting nearest inactive planets from %s", origin_planet.name)

        nearest_planets = self.get_nearest_planets(origin_planet, nr_range)
        planets = [planet for planet
                   in nearest_planets
                   if planet.player_state == galaxy.PlayerState.Inactive
                   and planet.player_rank >= self.config.minimum_inactive_target_rank
                   and planet.player_rank <= self.config.maximum_inactive_target_rank]
        return planets

    def spy_nearest_planets(self, origin_planet=None, nr_range=3):
        """Spy the nearest planets from origin"""

        if origin_planet is None:
            origin_planet = self.default_origin_planet

        self.logger.info("Getting nearest planets from %s", origin_planet.name)
        target_planets = self.get_nearest_planets(origin_planet, nr_range)

        for target_planet in target_planets:
            self.fleet_client.spy_planet(target_planet, self.config.spy_probes_count)

    def spy_nearest_inactive_planets(self, origin_planet=None, nr_range=3):
        """ Spy the nearest inactive planets from origin"""

        if origin_planet is None:
            origin_planet = self.default_origin_planet

        self.logger.info("Spying nearest inactive planets from %s", origin_planet.name)

        target_planets = self.get_nearest_inactive_planets(origin_planet, nr_range)

        for target_planet in target_planets:
            self.fleet_client.spy_planet(target_planet, self.config.spy_probes_count)

    def get_systems_in_range(self, nr_range, planet=None):
        """Return the systems in range"""

        systems = []
        if planet is None:
            planets = self.planets;
        else:
            planets = [planet]

        for p in planets:
            systems.append("%s:%s" % (p.coordinates.split(":")[0], p.coordinates.split(":")[1]))

            for i in range(1, nr_range + 1):
                previous_system = self.get_circular_system( int(p.coordinates.split(":")[1]) + i )
                later_system = self.get_circular_system( int(p.coordinates.split(":")[1]) - i )
                systems.append("%s:%s" % (p.coordinates.split(":")[0], str(previous_system)))
                systems.append("%s:%s" % (p.coordinates.split(":")[0], str(later_system)))

        # Return the list without duplicate systems in a random order
        res = list(set(systems))
        shuffle(res)

        return res

    def associate_systems_to_origin_planet(self, systems):
        """Associate systems to the nearest player planet"""

        associated_systems = []
        for system in systems:
            origin_planet = self.get_nearest_planet_to_coordinates(system + ":1", self.planets)
            associated_systems.append((system, origin_planet))

        return associated_systems

    def auto_spy_inactive_planets(self, nr_range=None):
        self.logger.info("Sending Spy Probes")

        # Stop if there is no fleet slot available
        slot_usage = self.fleet_client.get_fleet_slots_usage()

        used_slots = slot_usage[0]
        available_slots = slot_usage[1]

        # One slot is meant to stay free
        if used_slots >= available_slots-1:
            self.logger.error("There is no fleet slot available")
            return True

        if nr_range is None:
            nr_range = self.config.attack_range

        self.logger.info("Getting systems in range")
        systems = self.get_systems_in_range(nr_range, self.planet)
        self.logger.info("there is a total of %d systems in the range %d" % (len(systems), self.config.attack_range))
        # associated_systems = self.associate_systems_to_origin_planet(systems);
        check_count = 0

        start = time.time()

        # for planet in planets:

        #     try:
                # systems = [system[0] for system in associated_systems if system[1] == planet]
                # self.logger.info("Getting inactive planets in range(%d) from %s" % (len(systems), planet.name))

        for system in systems:

            try:
                # Check hostile activity every 35 systems
                if check_count > 35:
                    self.movement_bot.check_hostile_activity()
                    check_count = 0

                else:
                    check_count = check_count + 1

                target_planets = self.get_inactive_planets_in_systems([system])

                for index, target_planet in enumerate(target_planets):

                    # Exit after 20 minutes
                    if time.time() > (start + 20 * 60):
                        return False

                    # delay before sending mission
                    if index > 1:
                        # Delay - wait a random time before sending fleet, this makes the bot less detectable
                        delay = random.randint(self.config.spy_fleet_min_delay, self.config.spy_fleet_max_delay)
                        self.logger.info("Waiting for random time(%s seconds) before sending fleet " % delay)
                        time.sleep(delay)

                    while True:
                        result = self.fleet_client.spy_planet(target_planet, self.config.spy_probes_count)
                        if result == fleet.FleetResult.NoAvailableSlots:
                            delay = int(self.config.time_to_wait_for_probes / 8)
                            self.logger.info(
                                "Waiting %d seconds for spy probes to return and free up some slots" % delay)
                            time.sleep(delay)
                        else:
                            break

            except Exception as e:
                exception_message = traceback.format_exc()
                self.logger.error(exception_message)

        return False

    def get_circular_system(self, sysPos):
        maxSystm = self.config.server.systems
        return (sysPos - 1) % maxSystm + 1

