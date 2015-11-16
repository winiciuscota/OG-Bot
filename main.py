import re
import logging
from mechanize import Browser
from Hangar import Hangar
from Resources import Resources
import cookielib
import sys
from AuthenticationProvider import AuthenticationProvider

username = sys.argv[1]
password = sys.argv[2]

# universe 105
universe = sys.argv[3]

# preparando logger
logger = logging.getLogger('ogame-bot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('Starting the bot')
browser = AuthenticationProvider(username, password, universe).GetBrowser()

logger.info('Buscando naves')

resources = Resources(browser, universe)
res = resources.GetResources()

print res

for r in res:
    print r

hangar = Hangar(Browser, universe)
# ships = hangar.GetShips()
#
# print ships
# for ship in ships:
#     print ship
