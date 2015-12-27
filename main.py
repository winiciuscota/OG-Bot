import re
import logging
from mechanize import Browser
from hangar import Hangar
from buildings import Buildings
import buildings
from defense import Defense
import cookielib
import sys
from authentication import AuthenticationProvider
import ConfigParser
from general import General
from fleet import Fleet
import general

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

username = ''
password = ''
universe = ''

if len(sys.argv) < 4 :
    if cfg == []:
        logger.info('You must pass 3 arguments (username, password, universe) or write have a config file')
        exit()
    else:
        logger.info('Getting user info from config file')
        username = config.get('UserInfo', 'username')
        password = config.get('UserInfo', 'password')
        universe = config.get('UserInfo', 'universe')
else:
    username = sys.argv[1]
    password = sys.argv[2]
    universe = sys.argv[3]

browser = AuthenticationProvider(username, password, universe).get_browser()

general_client = General(browser, universe)
planets = general_client.get_planets()
building_client = Buildings(browser, universe)
fleet_client = Fleet(browser, universe)
logger.info('starting fleet client')
hangar_client = Hangar(browser, universe)
defense_client = Defense(browser, universe)


fleet_client.transport_resources(planets[0], planets[1], general.Resources(1000, 0, 0, 0))
