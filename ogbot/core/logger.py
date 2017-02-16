from base import BaseBot
from scraping import *
from core import defender


class LoggerBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config)
        self.movement_client = movement.Movement(browser, config)
        self.defense_client = defense.Defense(browser, config)
        self.hangar_client = hangar.Hangar(browser, config)
        self.general_client = general.General(browser, config)
        self.buildings_client = buildings.Buildings(browser, config)
        self.research_client = research.Research(browser, config)

        super(LoggerBot, self).__init__(browser, config, planets)

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

        planets = self.planets

        for planet in planets:
            planet.resources = self.general_client.get_resources(planet)
            planet.defenses = self.defense_client.get_defenses(planet)
            planet.fleet = self.hangar_client.get_ships(planet)
            planet.buildings = self.buildings_client.get_buildings(planet)
            planet.research = self.research_client.get_research(planet)

        total_resources = scraper.Resources(0, 0, 0)

        for planet in planets:
            total_resources.sum(planet.resources)

            self.logger.info("Planet %s:", planet)
            self.logger.info("Resources: [%s]", planet.resources)
            self.logger.info("Defenses: ")
            for defense in planet.defenses:
                self.print_item_order(defense)

            self.logger.info("Fleet: ")
            for ship in planet.fleet:
                self.print_item_order(ship)

            self.logger.info("Buildings: ")
            for buildings in planet.buildings:
                self.print_building_item_order(buildings)

        # We need the research output only once
        self.logger.info("Research: ")
        for research in planets[0].research:
            self.print_building_item_order(research)

        self.logger.info("Total of resources is: [%s]", total_resources)

        self.log_fleet_movement()

    def log_planets_in_same_system(self):
        """Log planets on same system"""

        planets = self.get_planets_in_same_ss()
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_planets(self):
        planets = self.get_nearest_planets(nr_range=15)
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_inactive_planets(self):
        planets = self.get_nearest_inactive_planets(nr_range=15)
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

    def log_index_page(self):
        """Log the index page for test purposes"""
        self.general_client.log_index_page()

    def print_item_order(self, item_order):
        if item_order.amount > 0:
            self.logger.info("\t%d %s(s)" % (item_order.amount, item_order.item.name))

    def print_building_item_order(self, item_order):
        if item_order.amount > 0:
            self.logger.info("\t%s - level %d" % (item_order.item.name, item_order.amount))


    def log_least_defended_planet(self):
        defender_bot = defender.DefenderBot(self.browser, self.config, self.planets)
        least_defended_planet = defender_bot.get_least_defended_planet()
        self.logger.info("Least defended planet is %s" % least_defended_planet.name)