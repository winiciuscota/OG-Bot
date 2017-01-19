from base import BaseBot
from ogbot.scraping import general, defense, scraper

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
       """

        planet_resources = self.general_client.get_resources(planet)

        defense_proportion_list = self.parse_defense_proportion(self.config.defense_proportion)
        available_defenses_proportion_list = filter(lambda x: x.item.cost < planet_resources,
                                                    defense_proportion_list)

        if self.check_exit_conditions_for_auto_build_defenses(planet, defense_proportion_list,
                                                              available_defenses_proportion_list,
                                                              planet_resources):
            return False

        defenses = self.defense_client.get_defenses(planet)

        defenses_relation = self.get_defenses_proportion_comparison_table(available_defenses_proportion_list, defenses)

        type_and_amount_to_build = self.get_type_and_amount_to_build(defenses_relation, planet_resources)

        self.defense_client.build_defense_to_planet(type_and_amount_to_build.item, type_and_amount_to_build.amount,
                                                    planet)

        return True

    def get_type_and_amount_to_build(self, defenses_relation, planet_resources):

        # the worst defense to build is the defense type that has the highest number of defenses
        # built by the desired proportion
        worst_defense_to_build = min(defenses_relation, key=lambda x: x.proportion_rate())
        # the best defense to build is the defense type that has the lowest number of defenses
        # built by the desired proportion
        best_defense_to_build = max(defenses_relation, key=lambda x: x.proportion_rate())

        if worst_defense_to_build == best_defense_to_build:
            target_amount_to_build = sys.maxint
        else:
            # Get necessary amount to build so that the defense proportion rates are equal
            target_amount = worst_defense_to_build.current_amount * best_defense_to_build.target_amount / \
                            worst_defense_to_build.target_amount
            target_amount_to_build = target_amount - best_defense_to_build.current_amount

        # Limit amount of the defenses to build according to the planet resources
        max_amount_by_budget = self.get_maximum_amount_of_defenses_by_budget(best_defense_to_build.item.cost,
                                                                             planet_resources)

        return scraper.ItemAction(best_defense_to_build.item, min(target_amount_to_build, max_amount_by_budget))

    def check_exit_conditions_for_auto_build_defenses(self, planet, defense_proportion_list,
                                                      available_defenses_proportion_list,
                                                      planet_resources):
        if len(available_defenses_proportion_list) == 1 \
                and available_defenses_proportion_list[0].item.id == defense.ROCKET_LAUNCHER.id \
                and len(defense_proportion_list) > 1:
            if self.config.spend_excess_metal_on_rl is False:
                self.logger.info("Can only build rocket launchers, and SpendExcessMetalOnRL is False")
                return True
            else:
                planet_resources.energy = 0
                self.logger.info("%s left" % planet_resources)
                self.logger.info("Spending excess metal on rocket launchers")

        if len(available_defenses_proportion_list) == 0:
            self.logger.info("No more resources on planet %s to continue building defenses" % planet.name)
            return True

        return False

    def get_least_defended_planet(self):
        least_defended_planet = min(self.planets, key=lambda x: self.get_defense_points_for_planet(x))
        return least_defended_planet

    def get_defense_points_for_planet(self, planet):
        defenses = self.defense_client.get_defenses(planet)
        defense_points = sum(
            [defense.DEFENSES_DATA.get(str(x.item.id)).cost.times(x.amount).get_points() for x in defenses])
        return defense_points

    def get_defenses_proportion_comparison_table(self, defenses_proportion_list, planet_defenses):
        defenses_proportion_comparison_table = []

        for defense_proportion in defenses_proportion_list:
            current_defense_amount = next(x.amount for x in planet_defenses if
                                          x.item.id == defense_proportion.item.id)
            defense_proportion_comparison = self.DefenseProportionComparison(defense_proportion.item,
                                                                             defense_proportion.amount,
                                                                             current_defense_amount)

            defenses_proportion_comparison_table.append(defense_proportion_comparison)

        return defenses_proportion_comparison_table

    @staticmethod
    def parse_defense_proportion(defense_proportion_str):
        parsed_defense_proportion = map(lambda x: scraper.ItemAction(defense.DEFENSES_DATA.get(filter(str.isalpha, x)),
                                                                     int(filter(str.isdigit, x))),
                                        defense_proportion_str)

        return filter(lambda x: x.item is not None and x.amount is not None, parsed_defense_proportion)

    @staticmethod
    def get_maximum_amount_of_defenses_by_budget(defense_type_cost, resources):

        max_by_metal = int(resources.metal / defense_type_cost.metal)

        max_by_crystal = int(resources.crystal / defense_type_cost.crystal) \
            if defense_type_cost.crystal != 0 else sys.maxint

        max_by_deuterium = int(resources.deuterium / defense_type_cost.deuterium) \
            if defense_type_cost.deuterium != 0 else sys.maxint

        return min(max_by_metal, max_by_crystal, max_by_deuterium)

    class DefenseProportionComparison:
        def __init__(self, defense_item, target_amount, current_amount):
            self.item = defense_item
            self.target_amount = target_amount
            self.current_amount = current_amount

        def proportion_rate(self):
            return self.target_amount / float(self.current_amount)
