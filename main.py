import re
import logging
from mechanize import Browser
from hangar import Hangar
from buildings import Buildings
from defense import Defense
from general import General
import cookielib
import sys
from authentication_provider import AuthenticationProvider

# setting up logger
logger = logging.getLogger('ogame-bot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if len(sys.argv) < 4:
    logger.info('You must pass 3 arguments (username, password, universe)')
    exit()

username = sys.argv[1]
password = sys.argv[2]

# universe 105
universe = sys.argv[3]

logger.info('Starting the bot')
browser = AuthenticationProvider(username, password, universe).get_browser()

general_client = General(browser, universe)
planets = general_client.get_planets()
defense_client = Defense(browser, universe)

# type = ('406', '100')
# defense_client.build_defense(type, planets[1])
for planet in planets:
    defense_client.auto_build_defenses(planet)
