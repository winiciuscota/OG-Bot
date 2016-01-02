import re
import logging
import sys
import ConfigParser
from bot import OgameBot

# setting up logger
logger = logging.getLogger('ogame-bot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Starting the bot')

config = ConfigParser.ConfigParser()
cfg = config.read('user.cfg')

if len(sys.argv) < 4 :
    if cfg == []:
        logger.info('You must pass 5 arguments (username, password, universe, mode, target plane) or write have a config file')
        exit()
    else:
        logger.info('Getting user info from config file')
        username = config.get('UserInfo', 'Username')
        password = config.get('UserInfo', 'Password')
        universe = config.get('UserInfo', 'Universe')
        mode = config.get('Settings', 'Mode')
        target_planet = config.get('Settings', 'TargetPlanet')
else:
    username = sys.argv[1]
    password = sys.argv[2]
    universe = sys.argv[3]
    mode = sys.argv[4]
    target_planet = sys.argv[5]

logger.info("Initializing bot")
bot = OgameBot(username, password, universe, target_planet)

switcher = {
    'auto_build_defenses': bot.auto_build_defenses,
    'get_defenses':bot.get_defenses,
    'get_ships': bot.get_ships,
    'get_planets': bot.get_planets,
    'transport_resources_to_planet' : bot.transport_resources_to_planet,
    'auto_build_structure_to_planet' : bot.auto_build_structure_to_planet
}

logger.info("Bot running on %s mode" % mode)
switcher.get(mode)()
