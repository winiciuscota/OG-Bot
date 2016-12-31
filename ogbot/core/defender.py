from base import BaseBot
from ogbot.scraping import defense, general
from ogbot.scraping.defense import *
import sys


class DefenderBot(BaseBot):
    def __init__(self, browser, config, planets):
        self.defense_client = defense.Defense(browser, config)
        self.general_client = general.General(browser, config)
        self.planets = planets
        super(DefenderBot, self).__init__(browser, config, planets)

    def auto_build_defenses(self):
        """Auto build defenses on all planets"""
        planets = self.planets
        for planet in planets:
            self.auto_build_defenses_to_planet(planet)

    def auto_build_defenses_to_planet(self, planet):

        while True:
            result = self.auto_build_defense_to_planet(planet)
            if result is False:
                break

    def auto_build_defense_to_planet(self, planet):
        """
               Automatically build defenses to the specified planet
               :param planet: planet to build defenses on
               :return:
       """

        defenses_relation = []

        planet_resources = self.general_client.get_resources(planet)

        defense_proportion_list = self.parse_defense_proportion(self.config.defense_proportion)
        available_defenses_proportion_list = filter(lambda x: x[0].cost < planet_resources, defense_proportion_list)

        if len(available_defenses_proportion_list) == 1 \
                and available_defenses_proportion_list[0][0] == ROCKET_LAUNCHER \
                and len(defense_proportion_list) > 1:
            if self.config.spend_excess_metal_on_rl is False:
                self.logger.info("Can only build rocket launchers, and SpendExcessMetalOnRL is False")
                return False
            else:
                self.logger.info("Spending excess metal on rocket launchers")

        if len(available_defenses_proportion_list) == 0:
            self.logger.info("No more resources on planet %s to continue building defenses" % planet.name)
            return False

        defenses = self.defense_client.get_defenses(planet)

        for defense_proportion in available_defenses_proportion_list:
            defense_relation = (defense_proportion[0],
                                defense_proportion[1],
                                next(x.amount for x in defenses if x.item.id == defense_proportion[0].id))
            defenses_relation.append(defense_relation)

        defenses_relation = map(lambda x: (x[0], x[1], x[2], x[1] / float(x[2])), defenses_relation)
        defenses_relation = sorted(defenses_relation, key=lambda x: x[1] / float(x[2]))

        better_defense_to_build = defenses_relation[-1]
        worst_defense_to_build = defenses_relation[0]

        if better_defense_to_build == worst_defense_to_build:
            target_amount_to_build = sys.maxint
        else:
            target_amount = worst_defense_to_build[2] * better_defense_to_build[1] / worst_defense_to_build[1]
            target_amount_to_build = target_amount - better_defense_to_build[2]

        max_amount_by_budget = self.get_maximun_amount_of_defenses_by_budget(better_defense_to_build[0].cost,
                                                                             planet_resources)

        amount_to_build = min(target_amount_to_build, max_amount_by_budget)
        self.defense_client.build_defense_to_planet(better_defense_to_build[0], amount_to_build, planet)

        return True

    @staticmethod
    def parse_defense_proportion(defense_proportion_str):
        parsed_defense_proportion = map(lambda x: (DEFENSES_DATA.get(filter(str.isalpha, x)),
                                                   int(filter(str.isdigit, x))), defense_proportion_str)

        return filter(lambda x: x[0] is not None and x[1] is not None, parsed_defense_proportion)

    @staticmethod
    def get_maximun_amount_of_defenses_by_budget(defense_type_cost, resources):

        max_by_metal = int(resources.metal / defense_type_cost.metal)

        if defense_type_cost.crystal == 0:
            max_by_crystal = sys.maxint
        else:
            max_by_crystal = int(resources.crystal / defense_type_cost.crystal)

        if defense_type_cost.deuterium == 0:
            max_by_deuterium = sys.maxint
        else:
            max_by_deuterium = int(resources.deuterium / defense_type_cost.deuterium)

        return min(max_by_metal, max_by_crystal, max_by_deuterium)
