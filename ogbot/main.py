import argparse
import logging
import sys
import traceback

from bot import OgameBot
from config import Config
from ogbot.sms import SMSSender
from scraping import authentication

parser = argparse.ArgumentParser()
parser.add_argument('-m', help='Mode in which to run the bot', nargs='+')
parser.add_argument('-r', help='Range of the bot')
parser.add_argument('-p', help='Origin planet')

args = parser.parse_args()
config = Config(args)

# setting up logger
logger = logging.getLogger('OGBot')
logger.setLevel(config.log_level)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Starting the bot')

auth_client = authentication.AuthenticationProvider(config)
browser = auth_client.get_browser()

bot = OgameBot(browser, config)

switcher = {
    'overview': bot.overview,
    'log_fleet_movement': bot.log_fleet_movement,
    'explore': bot.explore,
    'attack_inactive_planets': bot.attack_inactive_planets,
    'auto_build_defenses': bot.auto_build_defenses,
    'auto_build_defenses_to_planet': bot.auto_build_defenses_to_planet,
    'transport_resources_to_planet': bot.transport_resources_to_planet,
    'transport_resources_to_least_developed_planet':
        bot.transport_resources_to_least_developed_planet,
    'transport_resources_to_least_defended_planet':
        bot.transport_resources_to_least_defended_planet,
    'auto_build_structures': bot.auto_build_structures,
    'auto_research': bot.auto_research,
    'check_hostile_activity': bot.check_hostile_activity
}


for mode in config.mode:
    function = switcher.get(mode)
    if function is None:
        logger.warning("There is no mode named %s" % mode)
        logger.warning("The available modes are:")
        logger.warning("\toverview")
        logger.warning("\tlog_fleet_movement")
        logger.warning("\texplore")
        logger.warning("\tattack_inactive_planets")
        logger.warning("\tauto_build_defenses")
        logger.warning("\tauto_build_defenses_to_planet")
        logger.warning("\ttransport_resources_to_least_developed_planet")
        logger.warning("\ttransport_resources_to_least_defended_planet")
        logger.warning("\tauto_build_structures")
        logger.warning("\tauto_research")
    else:
        logger.info("Bot running in %s mode" % mode)
        try:
            function()
        except Exception as e:
            exception_message = traceback.format_exc()
            logger.error(exception_message)
            sms_sender = SMSSender(config)
            sms_sender.send_sms(exception_message)

logger.info("Quiting bot")
