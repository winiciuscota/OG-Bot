from base import BaseBot
from scraping import movement


class MovementBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.movement_scraper = movement.Movement(browser, config)

        super(MovementBot, self).__init__(browser, config, planets)

    def check_hostile_activity(self):
        fleet_movement = self.movement_scraper.get_fleet_movement()
        hostile_movements = filter(lambda x: not x.friendly, fleet_movement)
        if len(hostile_movements) == 0:
            self.logger.info("There is no hostile activity now")
        for hostile_movement in hostile_movements:
            self.logger.warning(hostile_movement)
            self.sms_sender.send_sms(hostile_movement)
