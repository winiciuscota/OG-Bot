import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urlparse
from enum import Enum


class Buildings:

    class Building_Types:
        """
        1. Mina de metal
        2. Mina de critsl
        3. Sintetizador de delterio
        4. Planta de energia solar
        5. Planta de fusao
        """
        MetalMine, CrystalMine, DeuteriumSynthesizer, SolarPlant, FusionReactor = range(1, 6)

    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser
        self.BUILDING_NAMES = {
            self.Building_Types.MetalMine :  'Metal Mine',
            self.Building_Types.CrystalMine :  'Crystal Mine',
            self.Building_Types.DeuteriumSynthesizer :  'Deutrium Synthesizer',
            self.Building_Types.SolarPlant :  'Solar Plant',
            self.Building_Types.FusionReactor :  'Fusion Reactor'
        }

    def get_buildings(self):
        self.logger.info('Getting resources data')
        url = self.url_provider.get_page_url('resources')
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

    def build_structure(self, type, planet):
        if self.construction_mode(planet):
            self.logger.info('Planet is already in construction mode')
            return
        self.build_structure_item(type, planet)

    def build_structure_item(self, type, planet = None):
        self.browser.select_form(name='form')
        self.browser.form.new_control('text','menge',{'value':'1'})
        self.browser.form.fixup()
        self.browser['menge'] = '1'

        self.browser.form.new_control('text','type',{'value':str(type)})
        self.browser.form.fixup()
        self.browser['type'] = str(type)

        self.browser.form.new_control('text','modus',{'value':'1'})
        self.browser.form.fixup()
        self.browser['modus'] = '1'

        self.logger.info("Submitting form")
        self.browser.submit()

    def construction_mode(self, planet = None):
        url = self.url_provider.get_page_url('resources', planet[1])
        self.logger.info('Opening url %s' % url)
        resp = self.browser.open(url)
        soup = BeautifulSoup(resp.read())
        return soup.find("div", {"class" : "construction"}) != None
