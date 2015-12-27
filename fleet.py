import util
from mechanize import Browser
import mechanize
from bs4 import BeautifulSoup
import re
import logging
import urlparse
from enum import Enum
from general import General


class Fleet:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def transport_resources(self, origin_planet, destination_planet, resources):
        self.send_fleet(origin_planet, destination_planet, resources, { 203 : 50}, 3)

    def send_fleet(self, origin_planet, destination_planet, resources, ships, mission):
        """
        Missions:
            15 - Expedition,
            7 - Colonization,
            8 - Recycle,
            3 - Transport,
            4 - Transfer,
            6 - Spy,
            5 - Defend planet,
            1 - Attack,
            2 - Alliance attack,
            9 - Destroy star
        """
        url = self.url_provider.get_page_url('fleet', origin_planet)
        self.logger.info('Opening fleet url: %s ' % url )
        resp = self.browser.open(url)

        try:
            self.browser.select_form(name='shipsChosen')
        except mechanize.FormNotFoundError:
            self.logger.error('The planet has no available ships')
            return

        soup = BeautifulSoup(resp.read())
        for ship, amount in ships.iteritems():
            self.browser["am" + str(ship)] = str(amount)

        self.browser.submit()

        self.browser.select_form(name='details')
        self.browser["galaxy"] = destination_planet.coordinates.split(':')[0]
        self.browser["system"] = destination_planet.coordinates.split(':')[1]
        self.browser["position"] = destination_planet.coordinates.split(':')[2]

        res = self.browser.submit()

        self.browser["mission"] = str(mission)
        self.browser["metal"] = str(resources.metal)
        self.browser["crystal"] = str(resources.crystal)
        self.browser["deuterium"] = str(resources.deuterium)
        print res.read()
