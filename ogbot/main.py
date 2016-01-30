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
    You must have the following data on the user.cfg
    
    [UserInfo]
    username = your_username
    password = your_password
    universe = your_universe

    [Settings]
    DefaultMode = transport_resources_to_planet
    DefaultOriginPlanet = origin_planet_name
    AttackRange = 10
    HowLongToWaitForProbes = 60 
"""

if cfg == []:
    print WRONG_ARGUMENTS_MESSAGE
    exit()
else:
    logger.info('Getting user info from config file')
    username = config.get('UserInfo', 'Username')
    password = config.get('UserInfo', 'Password')
    universe = config.get('UserInfo', 'Universe')
    mode = config.get('Settings', 'DefaultMode')
    origin_planet_name = config.get('Settings', 'DefaultOriginPlanet')
    attack_range = config.get('Settings', 'AttackRange')
    time_to_wait_for_probes = config.get('Settings', 'HowLongToWaitForProbes')
    spy_report_life = config.get('Settings', 'SpyReportLife')
    
if len(sys.argv) > 1 :
    mode = sys.argv[1]
    
if len(sys.argv) > 2 :
    origin_planet_name = sys.argv[2]

logger.info("Initializing bot")

bot = OgameBot(username, password, universe, origin_planet_name, attack_range, time_to_wait_for_probes, spy_report_life)

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
    'log_index_page' : bot.log_index_page,
    'log_game_datetime' : bot.log_game_datetime,
    'auto_attack_inactive_planets' : bot.auto_attack_inactive_planets,
    'log_fleet_movement' : bot.log_fleet_movement,
    'auto_spy_inactive_planets' : bot.auto_spy_inactive_planets,
    'clear_inbox' : bot.clear_inbox
}

logger.info("Bot running on %s mode" % mode)
switcher.get(mode)()
logger.info("Quiting bot")
