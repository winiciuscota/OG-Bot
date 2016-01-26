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

    def get_ships(self, planet):
        self.logger.info('Getting shipyard data for planet %s' % planet)
        url = self.url_provider.get_page_url('shipyard', planet)
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read(), "lxml")
        refs = soup.findAll("span", { "class" : "textlabel" })

        ships = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                ship_raw_data = re.sub('  +', '', aux).encode('utf8')
                ship_id = ref.parent.parent.parent['ref']
                ship_data = ship_raw_data.split('\n');
                ship_data.append(ship_id)
                ships.append( tuple(ship_data) )

        ships = map(tuple, map(util.sanitize, [filter(None, i) for i in ships]))
        return [Ship(ship[0], ship[2], ship[1]) for ship in ships]


class Ship(object):
    def __init__(self, name, id, amount):
        self.name = name
        self.id = id
        self.amount = amount

    def __str__(self):
        return "[Description: %s, Id: %s, Amount: %s ]" % (self.name, self.id, self.amount)
