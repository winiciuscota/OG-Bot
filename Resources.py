from OgameUtil import UrlProvider
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging

class Resources:
    def __init__(self, browser, universe):
        self.urlProvider = UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def GetResources(self):
        self.logger.info('recuperando recursos')
        url = self.urlProvider.GetPageUrl('resources')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })

        res = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                res.append( tuple(shipData.split('\n')))

        res = map(tuple, map(sanitize, [filter(None, i) for i in res]))
        return res

def sanitize(t):
    for i in t:
        try:
            yield int(i)
        except ValueError:
            yield i
