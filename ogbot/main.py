import re
import logging
import sys

from bot import OgameBot
from logger import LoggerBot
from config import Config


# setting up logger
logger = logging.getLogger('OGBot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Starting the bot')

config = Config(sys.argv)
bot = OgameBot(config)
logger_bot = LoggerBot(config)

switcher = {
    #Log functions
    'log_defenses':logger_bot.log_defenses,
    'log_ships': logger_bot.log_ships,
    'log_planets': logger_bot.log_planets,
    'log_index_page' : logger_bot.log_index_page,
    'log_game_datetime' : logger_bot.log_game_datetime,
    'log_planets_in_same_system' : logger_bot.log_planets_in_same_system,
    'log_nearest_planets' : logger_bot.log_nearest_planets,
    'log_nearest_inactive_planets' : logger_bot.log_nearest_inactive_planets,
    'log_spy_reports' : logger_bot.log_spy_reports,
    'log_fleet_movement' : logger_bot.log_fleet_movement,
    'log_fleet_slot_usage' : logger_bot.log_fleet_slot_usage,
    'overview' : logger_bot.log_overview,

    'auto_build_defenses': bot.auto_build_defenses,
    'auto_build_structures' : bot.auto_attack_inactive_planets,
    'auto_build_structure_to_planet' : bot.auto_build_structure_to_planet,
    "auto_build_defenses_to_planet" : bot.auto_build_defenses_to_planet,

    'spy_nearest_planets' : bot.spy_nearest_planets,
   
    'transport_resources_to_planet' : bot.transport_resources_to_planet,
    'spy_nearest_inactive_planets' : bot.spy_nearest_inactive_planets,
    'attack_inactive_planets_from_spy_reports' : bot.attack_inactive_planets_from_spy_reports,
    'auto_attack_inactive_planets' : bot.auto_attack_inactive_planets,
    'auto_spy_inactive_planets' : bot.auto_spy_inactive_planets,
    'auto_send_expeditions' : bot.auto_send_expeditions,
    'explore' : bot.explore,
    'clear_inbox' : bot.clear_inbox
}

logger.info("Bot running on %s mode" % config.mode)
switcher.get(config.mode)()
logger.info("Quiting bot")
