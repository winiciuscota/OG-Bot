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

WRONG_ARGUMENTS_MESSAGE = """
You must pass at least 3 arguments:
    username - name of the user
    password - password of the user
    universe - universe id (e.g. 101)
    mode (optional) - the mode in which the bot should run, defaults to get_planets
    target plane (optional) - target planet if the mode requires some, defaults to the first planet
Alternatively you can write a cfg file, the user.cfg file should look like this:
    [UserInfo]
    username = your_username
    password = your_password
    universe = your_universe

    [Settings]
    Mode = transport_resources_to_planet
    TargetPlanet = target_planet_name
"""

if len(sys.argv) < 4 :
    if cfg == []:
        print WRONG_ARGUMENTS_MESSAGE
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
    mode = sys.argv[4] if len(sys.argv) >= 5 else "overview"
    target_planet = sys.argv[5] if len(sys.argv) >= 6 else None

logger.info("Initializing bot")

bot = OgameBot(username, password, universe, target_planet)

switcher = {
    'log_defenses':bot.log_defenses,
    'log_ships': bot.log_ships,
    'log_planets': bot.log_planets,
    'overview' : bot.log_overview,
    'auto_build_defenses': bot.auto_build_defenses,
    'auto_build_structures' : bot.auto_build_structures,
    'auto_build_structure_to_planet' : bot.auto_build_structure_to_planet,
    "auto_build_defenses_to_planet" : bot.auto_build_defenses_to_planet,
    'transport_resources_to_planet' : bot.transport_resources_to_planet,
    'log_planets_in_same_system' : bot.log_planets_in_same_system,
    'log_nearest_planets' : bot.log_nearest_planets,
    'log_nearest_inactive_planets' : bot.log_nearest_inactive_planets,
    'spy_nearest_planets' : bot.spy_nearest_planets,
    'spy_nearest_inactive_planets' : bot.spy_nearest_inactive_planets,
    'log_spy_reports' : bot.log_spy_reports,
    'attack_inactive_planets_from_spy_reports' : bot.attack_inactive_planets_from_spy_reports,
    'log_index_page' : bot.log_index_page
}

logger.info("Bot running on %s mode" % mode)
switcher.get(mode)()
logger.info("Quiting bot")
