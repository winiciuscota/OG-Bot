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
                    'print_ressources' : {
                        'enable': True,
                        'priority': 10,
                        'delay': 10,
                        'function': bot.print_ressources
                    },
                    'auto_build_structures': {
                        'enable': True,
                        'priority': 1,
                        'delay': 180,
                        'function': bot.auto_build_structures
                    },
                    'attack_inactive_planets': {
                        'enable': True,
                        'priority': 1,
                        'delay': 5400,
                        'function': bot.attack_inactive_planets
                    },
                    'auto_research': {
                        'enable': True,
                        'priority': 1,
                        'delay': 3600,
                        'function': bot.auto_research
                    }
            }

            self.schedules = SCHEDULES
            self.logger.info("Scheduler mode enabled")
            self.scheduler.enter(1, 1, bot.overview, ())

            for schedule in SCHEDULES:
                if SCHEDULES[schedule]['enable']:
                    self.set_schedule(schedule)
                    #self.scheduler.enter(   SCHEDULES[schedule]['delay'],
                    #                        SCHEDULES[schedule]['priority'],
                    #                        SCHEDULES[schedule]['function'], ())
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
                self.scheduler.enter(   delay, piority,
                                        self.set_schedule, (
                                            function, delay, priority))
