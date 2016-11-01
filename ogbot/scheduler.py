from bot import OgameBot
import sched
import time
import logging

class Scheduler():
    def __init__(self, browser, config):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.config = config
        self.config.scheduler = self.scheduler
        bot = OgameBot(browser, config)
        self.logger = logging.getLogger('OGBot')

        if self.config.scheduler:
            SCHEDULES = {
                    'print_resources' : {
                        'enable':   self.config.schedules['print_resources']['enable'],
                        'priority': 1,
                        'delay': self.config.schedules['print_resources']['delay'],
                        'function': bot.print_resources
                    },
                    'auto_build_structures': {
                        'enable': self.config.schedules['auto_build_structures']['enable'],
                        'priority': 3,
                        'delay': self.config.schedules['auto_build_structures']['delay'],
                        'function': bot.auto_build_structures
                    },
                    'attack_inactive_planets': {
                        'enable': self.config.schedules['attack_inactive_planets']['enable'],
                        'priority': 2,
                        'delay': self.config.schedules['attack_inactive_planets']['delay'],
                        'function': bot.attack_inactive_planets
                    },
                    'auto_research': {
                        'enable': self.config.schedules['auto_research']['enable'],
                        'priority': 3,
                        'delay': self.config.schedules['auto_research']['delay'],
                        'function': bot.auto_research
                    },
                    'transport_resources_to_weaker_planet': {
                        'enable': self.config.schedules['transport_resources_to_weaker_planet']['enable'],
                        'priority': 3,
                        'delay': self.config.schedules['transport_resources_to_weaker_planet']['delay'],
                        'function': bot.transport_resources_to_weaker_planet
                    },
                    'auto_build_defenses': {
                        'enable': self.config.schedules['auto_build_defenses']['enable'],
                        'priority': 3,
                        'delay': self.config.schedules['auto_build_defenses']['delay'],
                        'function': bot.auto_build_defenses
                    }
            }

            self.schedules = SCHEDULES
            self.logger.info("Scheduler mode enabled")
            self.scheduler.enter(1, 1, bot.overview, ())

            for schedule in SCHEDULES:
                if SCHEDULES[schedule]['enable']:
                    self.set_schedule(schedule)

            self.scheduler.run()

    def set_schedule(self, function, delay=None, priority=None, retry=True):
        if delay is None:
            delay = self.schedules[function]['delay']
        if priority is None:
            priority = self.schedules[function]['priority']

        if function in self.schedules:
            self.logger.debug(
                "Adding function to schedule %s, priorty %i, delay %i seconds" % (function, priority, delay))

            self.scheduler.enter(   delay, priority,
                                    self.schedules[function]['function'], ())
            if retry:
                self.scheduler.enter(   delay, priority,
                                        self.set_schedule, (
                                            function, delay, priority))
