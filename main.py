import re
import logging
from mechanize import Browser
from Hangar import Hangar
from Buildings import Buildings
from Defense import Defense
from General import General
import cookielib
import sys
from AuthenticationProvider import AuthenticationProvider

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
browser = AuthenticationProvider(username, password, universe).GetBrowser()

client = Buildings(browser, universe)
client.Build()

#
# hangar = Hangar(browser, universe)
# ships = hangar.GetShips()
# print ships


# defense = Defense(browser, universe)
# defense.build_defense()
# defenses = defense.GetDefenses()
# print defenses
