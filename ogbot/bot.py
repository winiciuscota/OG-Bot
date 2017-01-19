import time
import logging

from scraping import general
from core import *

class OgameBot(object):
    def __init__(self, browser, config):
        # Authenticate and get browser instance
        self.config = config
        self.logger = logging.getLogger('OGBot')

        # Get planets and remove excluded planets in the config file
        planets = general.General(browser, config).get_planets()
        planets = filter(lambda x: x.name.lower() not in config.excluded_planets, planets)

        self.attacker_bot = attacker.AttackerBot(browser, config, planets)
        self.defender_bot = defender.DefenderBot(browser, config, planets)
        self.spy_bot = spy.SpyBot(browser, config, planets)
        self.expeditionary_bot = expeditionary.ExpeditionaryBot(browser, config, planets)
        self.logger_bot = logger.LoggerBot(browser, config, planets)
        self.transporter_bot = transporter.TransporterBot(browser, config, planets)
        self.builder_bot = builder.BuilderBot(browser, config, planets)
        self.messages_bot = messages.MessagesBot(browser, config, planets)
        self.researcher_bot = researcher.ResearcherBot(browser, config, planets)

    def explore(self):
        self.expeditionary_bot.auto_send_expeditions()
        self.attack_inactive_planets()

    def attack_inactive_planets(self):
        reports = self.messages_bot.get_valid_spy_reports_from_inactive_targets()

        if len(reports) == 0:
            self.logger.info("There isn't any valid spy reports from inactive targets")
            self.logger.info("Scanning for new targets")
            self.spy_bot.auto_spy_inactive_planets(self.config.attack_range)
            self.logger.info("Waiting %f seconds for probes to return" % self.config.time_to_wait_for_probes)
            time.sleep(self.config.time_to_wait_for_probes)
            reports = self.messages_bot.get_valid_spy_reports_from_inactive_targets()
            self.attacker_bot.attack_inactive_planets_from_spy_reports(reports)
        else:

            self.attacker_bot.attack_inactive_planets_from_spy_reports(reports)

        self.messages_bot.clear_spy_reports()

    def overview(self):
        self.logger_bot.log_overview()

    def log_fleet_movement(self):
        self.logger_bot.log_fleet_movement()

    def transport_resources_to_least_defended_planet(self):
        least_defended_planet = self.defender_bot.get_least_defended_planet()
        self.transporter_bot.transport_resources_to_planet(least_defended_planet)

    def transport_resources_to_planet(self):
        self.transporter_bot.transport_resources_to_planet()

    def transport_resources_to_weaker_planet(self):
        weaker_planet = self.builder_bot.get_planet_for_construction()
        self.transporter_bot.transport_resources_to_planet(weaker_planet)

    def auto_build_defenses(self):
        self.defender_bot.auto_build_defenses()

    def auto_build_defenses_to_planet(self):
        self.defender_bot.auto_build_defenses_to_planet()

    def auto_build_structures(self):
        self.builder_bot.auto_build_structures()

    def auto_research(self):
        self.researcher_bot.auto_research_next_item()
