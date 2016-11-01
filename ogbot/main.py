import argparse
import logging
import sys
import time
from bot import OgameBot
from config import Config
from scheduler import Scheduler

from scraping import authentication


parser = argparse.ArgumentParser()
parser.add_argument('-m', help='Mode in which to run the bot', nargs='+')
parser.add_argument('-r', help='Range of the bot')
parser.add_argument('-s', action='store_true', help='Activate scheduler mode')
parser.add_argument('-p', help='Origin planet')

args = parser.parse_args()

# setting up logger
logger = logging.getLogger('OGBot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Starting the bot')

config = Config(args)

auth_client = authentication.AuthenticationProvider(config)
browser = auth_client.get_browser()

bot = None
if config.scheduler:
    scheduler = Scheduler(browser, config)
else:
    bot = OgameBot(browser, config)

switcher = {
    'overview': bot.overview,
    'explore': bot.explore,
    'attack_inactive_planets': bot.attack_inactive_planets,
    'auto_build_defenses': bot.auto_build_defenses,
    'auto_build_defenses_to_planet': bot.auto_build_defenses_to_planet,
    'transport_resources_to_planet': bot.transport_resources_to_planet,
    'transport_resources_to_weaker_planet': bot.transport_resources_to_weaker_planet,
    'auto_build_structures': bot.auto_build_structures,
    'auto_research': bot.auto_research
}

if not config.scheduler:
    for mode in config.mode:
        function = switcher.get(mode)
        if function is None:
            logger.warning("There is no mode named %s" % mode)
            logger.warning("The available modes are:")
            logger.warning("\toverview")
            logger.warning("\texplore")
            logger.warning("\tattack_inactive_planets")
            logger.warning("\tauto_build_defenses")
            logger.warning("\tauto_build_defenses_to_planet")
            logger.warning("\ttransport_resources_to_weaker_planet")
            logger.warning("\tauto_build_structures")
            logger.warning("\tauto_research")
        else:
            logger.info("Bot running in %s mode" % mode)
            function()
logger.info("Quiting bot")
