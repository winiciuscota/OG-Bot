from bot import OgameBot

class LoggerBot(OgameBot):
    """Logging functions for the bot"""

    def log_planets(self):
        """Log planets info"""
        planets = self.planets
        self.logger.info("Logging planets")
        for planet in planets:
            self.logger.info(planet)

    def log_defenses(self):
        """Log defenses data"""
        planets = self.planets
        self.logger.info("Logging defenses")
        for planet in planets:
            self.logger.info(self.defense_client.get_defenses(planet))

    def log_ships(self):
        """Log ships info"""

        planets = self.planets
        for planet in planets:
            ships = self.hangar_client.get_ships(planet)
            self.logger.info("Logging ships for planet %s:" % planet.name)
            for ship in ships:
                self.logger.info(ship)

    def log_overview(self):
        """Log planets overview"""

        planets = self.general_client.get_planets_overview();
        
        for planet in planets:
            self.logger.info("Planet %s:", planet)
            self.logger.info("Resources: [%s]", planet.resources)
            self.logger.info("Defenses: %s", planet.defenses)
            self.logger.info("Fleet: %s", planet.fleet)

    def log_planets_in_same_system(self):
        """Log planets on same system"""

        planets = self.get_planets_in_same_ss()
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_planets(self):
        planets = self.get_nearest_planets(nr_range =  15)
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_inactive_planets(self):
        planets = self.get_nearest_inactive_planets(nr_range = 15)
        for planet in planets:
            self.logger.info(planet)

    def log_spy_reports(self):
        spy_reports = self.get_spy_reports()
        for spy_report in spy_reports:
            self.logger.info("Date:%s - %s" % (spy_report.report_datetime, spy_report))

    def log_game_datetime(self):
        datetime = self.general_client.get_game_datetime()
        self.logger.info(datetime)

    def log_fleet_movement(self):
        movements = self.movement_client.get_fleet_movement()
        for movement in movements:
            self.logger.info(movement)

    def log_fleet_slot_usage(self):
        slot_usage = self.fleet_client.get_fleet_slots_usage()
        self.logger.info(slot_usage)




