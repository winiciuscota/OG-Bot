from base import *
from scraping import fleet, movement, general, scraper, hangar
import random
import time

class AttackerBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config, planets)
        self.general_client = general.General(browser, config)
        self.movement_client = movement.Movement(browser, config)
        self.hangar_client = hangar.Hangar(browser, config)

        super(AttackerBot, self).__init__(browser, config, planets)

    def attack_inactive_planet(self, origin_planet, target_planet):
        origin_planet.ships = self.hangar_client.get_ships(origin_planet)
        result = self.fleet_client.attack_inactive_planet(origin_planet, target_planet)
        return result

    def attack_inactive_planets_from_spy_reports(self, reports):

        # Stop if there is no fleet slot available
        slot_usage = self.fleet_client.get_fleet_slots_usage()

        used_slots = slot_usage[0]
        available_slots = slot_usage[1]

        if used_slots >= available_slots:
            self.logger.warning("There is no fleet slot available")
            return True

        movements = [fleet_movement.destination_coords for fleet_movement
                     in self.movement_client.get_fleet_movement()]

        self.logger.info("Got %d reports" % len(reports))

        inactive_planets = [report for report
                            in set(reports)
                            # Get reports from inactive players only
                            if report.player_state == scraper.PlayerState.Inactive
                            # Don't attack planets that are already being attacked
                            and report.coordinates not in movements
                            # Only attack planets with enough resources
                            and get_target_value(report) >= self.config.min_res_to_attack
                            # Don't attack defended planets
                            # and report.defenses == 0
                            and report.fleet == 0]

        self.logger.info("Found %d recent spy reports of inactive players" % len(inactive_planets))

        distinct_inactive_planets = get_distinct_targets(inactive_planets)

        # Attack high value targets first
        targets = sorted(distinct_inactive_planets, key=get_target_value, reverse=True)

        predicted_loot = 0
        assault_fleets_count = 0

        for target in targets:

            try:
                if target.defenses != 0:
                    self.logger.warning("Found an inactive defended planet %s(%s) with %s" % (target.planet_name, target.coordinates, target.resources))
                    continue
                if used_slots < available_slots:
                    self.logger.info("Slot usage: %d/%d" % (used_slots, slot_usage[1]))

                    # Get the nearest planets from target
                    nearest_planets = BaseBot.get_nearest_planets_to_target(target, self.planets)
                    noShips = 0

                    # Attempt attack from each planet until success
                    for planet in nearest_planets:
                        result = self.attack_inactive_planet(planet, target)

                        if result == fleet.FleetResult.Success:
                            predicted_loot += target.get_loot()
                            used_slots += 1
                            assault_fleets_count += 1

                            # Delay - wait a random time before sending fleet, this makes the bot less detectable
                            delay = random.randint(self.config.attack_fleet_min_delay, self.config.attack_fleet_max_delay)
                            self.logger.info("Waiting for %s seconds" % delay)
                            time.sleep(delay)
                            break

                        if result == fleet.FleetResult.NoAvailableSlots:
                            self.logger.warning("There is no fleet slot available")
                            self.logger.info("Predicted loot is %s" % predicted_loot)
                            return True

                        # Count the number of planets without any ship left
                        if result == fleet.FleetResult.NoAvailableShips:
                            noShips = noShips + 1

                            # If no ships on all planets, stop attacking
                            if noShips >= len(nearest_planets):
                                self.logger.warning("No ships on all planets, attack finished")
                                return True


                else:
                    self.logger.info("No more available slots")
                    break

            except Exception as e:
                print e
                pass


            # Update fleet slot counters (could change for various reasons)
            slot_usage = self.fleet_client.get_fleet_slots_usage()
            used_slots = slot_usage[0]
            available_slots = slot_usage[1]


        self.logger.info("Predicted loot is %s" % int(predicted_loot))
        self.sms_sender.send_sms("%d assault fleets were deployed, the predicted loot is %s"
                                 % (assault_fleets_count, predicted_loot))
        return True

    def auto_attack_inactive_planets(self):
        result = self.attack_inactive_planets_from_spy_reports()
        if not result:
            error = self.spy_bot.auto_spy_inactive_planets(self.config.attack_range)

            if error:
                return True

            self.logger.info("Waiting %f seconds for probes to return" % self.config.time_to_wait_for_probes)
            time.sleep(self.config.time_to_wait_for_probes)
            self.attack_inactive_planets_from_spy_reports()


    # Sorts planets by loot then proximity
    def planetsByLootThenProximity(self, target):

        for planet in self.planets:
            planet.ships = self.hangar_client.get_ships(planet)
            planet.loot = self.fleet_client.get_attack_loot(planet, target)

        ordered_planets = sorted(self.planets, key=lambda x: x.loot, reverse=True)
        maxLoot = max(self.planets, key=lambda x: x.loot)

        planets_by_loot = []
        cList = []
        last = None

        for planet in ordered_planets:

            loot = planet.loot

            if last is None:
                last = loot

            if loot == last:
                cList.append(planet)

            else:
                planets_by_loot.append(cList)
                cList = [ planet ]

            last = loot

        planets_by_loot.append(cList)


        origin_planets = [planet
                          for planets in planets_by_loot
                          for planet in BaseBot.get_nearest_planets_to_target(target, planets)]

        return origin_planets


def get_distinct_targets(targets):
    """Given a list that possibly contains repeated targets, returns a list of distinct targets"""
    dict_targets = {}
    for obj in targets:
        dict_targets[obj.coordinates] = obj
    distinct_targets = dict_targets.values()
    return distinct_targets


def get_target_value(target):
    """Get the value of a target by its resources"""
    return target.resources.total() * target.loot
