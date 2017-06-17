from base import BaseBot
from scraping import movement, fleet


class MovementBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.fleet_client = fleet.Fleet(browser, config, planets)
        self.movement_scraper = movement.Movement(browser, config)

        super(MovementBot, self).__init__(browser, config, planets)

    def check_hostile_activity(self):
        fleet_movement = self.movement_scraper.get_fleet_movement()
        hostile_movements = filter(lambda x: not x.friendly and x.mission in {'attack', 'allianceAttack'}, fleet_movement)

        if len(hostile_movements) == 0:
            self.logger.info("There is no hostile activity now")

        targets = {}

        for hostile_movement in hostile_movements:
            self.logger.warning(hostile_movement)
            self.logger.warning('Incoming attack on planet %s, attempting fleet escape', hostile_movement.destination_name)
            self.sms_sender.send_sms(hostile_movement)

            cTarget = hostile_movement.destination_coords
            target = self.get_player_planet_by_coordinates(cTarget)
            target.safe = False
            targets[cTarget + str(hostile_movement.isMoon)] = target

        for coords, target in targets.iteritems():
            self.fleet_client.fleet_escape(target)
