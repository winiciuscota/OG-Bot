import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging


class Defense:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.br = browser

    def get_defenses(self, planet = None):
        self.logger.info('Getting defense data')
        url = self.url_provider.get_page_url('defense', planet)
        self.logger.info('The defense url is ' + url)
        res = self.br.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })

        defenses = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                defenses.append( tuple(shipData.split('\n')) )

        defenses = map(tuple, map(util.sanitize, [filter(None, i) for i in defenses]))
        return defenses

    def auto_build_defenses(self, planet = None):
        """
        401. missile launcher
        402. light cannon
        404. gauss cannon
        406. plasma
        """
        defense_types = [('406', '100'), ('404', '100'), ('402', '1500'), ('401', '3000')]

        self.redirect_to_page(planet)
        for defense in defense_types:
            self.build_defense_item(defense, planet)


    def redirect_to_page(self, planet = None):
        url = self.url_provider.get_page_url('defense', planet)
        self.logger.info("Redirecting to page %s" % url)
        self.br.open(url)

    def build_defense(self, defense, planet = None):
        self.redirect_to_page(planet)

        try:
            self.build_defense_item(defense, planet)
        except Exception as e:
            self.logger.info(e)

    def build_defense_item(self, defense, planet = None):
        self.logger.info("building %s %s on planet %s" % (defense[1], defense[0], planet))
        self.logger.info("Writing data to form")
        self.br.select_form(name='form')
        self.br.form.new_control('text','menge',{'value': defense[1]})
        self.br.form.fixup()
        self.br['menge'] = defense[1]
        self.br.form.new_control('text','type',{'value':defense[0]})
        self.br.form.fixup()
        self.br['type'] = defense[0]
        self.br.form.new_control('text','modus',{'value':'1'})
        self.br.form.fixup()
        self.br['modus'] = '1'
        self.br.submit()

    def get_ships_in_construction(self):
        soup = BeautifulSoup(res.br.response.read())
        defenses = soup.findAll("span", { "class" : "count undermark" })
