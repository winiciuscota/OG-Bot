from Util import UrlProvider
import Util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging


class Defense:
    def __init__(self, browser, universe):
        self.urlProvider = UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.br = browser

    def GetDefenses(self):
        self.logger.info('Getting defense data')
        url = self.urlProvider.GetPageUrl('defense')
        res = self.br.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })

        defenses = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                defenses.append( tuple(shipData.split('\n')) )

        defenses = map(tuple, map(Util.sanitize, [filter(None, i) for i in defenses]))
        return defenses

    def build_defense(self, planet = None):
        """
        406. plasma
        402. light cannon
        """
        
        url = self.urlProvider.GetPageUrl('defense', planet)
        self.logger.info('Building defense')
        self.logger.info('The defense url is: ' + url)
        resp = self.br.open(url)
            self.br.select_form(name='form')
            self.br.form.new_control('text','menge',{'value':'100'})
            self.br.form.fixup()
            self.br['menge'] = '100'

            self.br.form.new_control('text','type',{'value':t})
            self.br.form.fixup()
            self.br['type'] = t

            self.br.form.new_control('text','modus',{'value':'1'})
            self.br.form.fixup()
            self.br['modus'] = '1'

            self.br.submit()
