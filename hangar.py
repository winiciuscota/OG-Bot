import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging


class Hangar:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_ships(self):
        self.logger.info('Getting shipyard data')
        url = self.url_provider.GetPageUrl('shipyard')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })

        ships = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                ships.append( tuple(shipData.split('\n')) )

        ships = map(tuple, map(Util.sanitize, [filter(None, i) for i in ships]))
        return ships
