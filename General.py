from Util import UrlProvider
import Util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging

class General:
    def __init__(self, browser, universe):
        self.urlProvider = UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def GetResources(self):
        self.logger.info('Getting resources data')
        url = self.urlProvider.GetPageUrl('resources')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())

        resources = []
        metal = int(soup.find(id='resources_metal').text.replace('.',''))
        resources.append({'metal': metal })
        crystal = int(soup.find(id='resources_crystal').text.replace('.',''))
        resources.append({'crystal': crystal })
        deuterium = int(soup.find(id='resources_deuterium').text.replace('.',''))
        resources.append({'deuterium': deuterium })
        energy = int(soup.find(id='resources_energy').text.replace('.',''))
        resources.append({'energy': energy })
        return resources
