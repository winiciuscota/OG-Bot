import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urlparse


class Buildings:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_buildings(self):
        self.logger.info('Getting resources data')
        url = self.url_provider.GetPageUrl('resources')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })

        res = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                res.append( tuple(shipData.split('\n')))

        res = map(tuple, map(Util.sanitize, [filter(None, i) for i in res]))
        return res

    def build(self, planet = None):
        """
        Build defense for all resources on the planet
        1. plasma
        2. gauss
        3. heavy cannon
        4. light cannon
        5. rocket launcher
        """
        url = self.url_provider.GetPageUrl('resources', planet)
        resp = self.browser.open(url)
        soup = BeautifulSoup(resp.read())
        attr = soup.find("a", { "class" : "fastBuild tooltip js_hideTipOnMobile" })['onclick']
        token = urlparse.parse_qs(attr.split("'")[1])['token']

        # Tipos
        # 1. Mina de metal
        # 2. Mina de critsl
        # 3. Sintetizador de delterio
        # 4. Planta de energia solar
        # 5. Planta de fusao
        type = '1'

        self.browser.select_form(name='form')
        self.browser.form.new_control('text','menge',{'value':'1'})
        self.browser.form.fixup()
        self.browser['menge'] = '1'

        self.browser.form.new_control('text','type',{'value':type})
        self.browser.form.fixup()
        self.browser['type'] = type

        self.browser.form.new_control('text','modus',{'value':'1'})
        self.browser.form.fixup()
        self.browser['modus'] = '1'

        # self.browser.form.new_control('text','token',{'value':token})
        # self.browser.form.fixup()
        # self.browser['token'] = str(token)

        self.browser.submit()
