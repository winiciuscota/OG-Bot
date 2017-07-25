from bs4 import BeautifulSoup
import urlparse
import datetime
from scraper import *


class General(Scraper):
    def log_index_page(self):
        """Logs the index page, used for test purposes"""
        url = self.url_provider.get_page_url('overview')
        res = self.open_url(url)
        self.logger.info(res.read())

    def get_game_datetime(self):
        url = self.url_provider.get_page_url('overview')
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        datetime_data = soup.find("li", {"class": "OGameClock"}).text
        game_datetime = datetime.datetime.strptime(datetime_data, "%d.%m.%Y %H:%M:%S")
        return game_datetime

    def get_resources(self, planet):
        self.logger.debug('Getting resources data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('resources', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        metal = int(soup.find(id='resources_metal').text.replace('.', ''))
        crystal = int(soup.find(id='resources_crystal').text.replace('.', ''))
        deuterium = int(soup.find(id='resources_deuterium').text.replace('.', ''))
        energy = int(soup.find(id='resources_energy').text.replace('.', ''))

        return Resources(metal, crystal, deuterium, energy)

    def get_planets(self):
        self.logger.info('Getting planets')
        url = self.url_provider.get_page_url('resources')

        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        elems = soup(attrs={'class': "smallplanet"})
        links = soup(attrs={'class': ["planetlink", 'moonlink']})
        planets = []

        for elem in elems:
            link = elem.find('a', {"class": "planetlink"})
            mlink = elem.find('a', {"class": "moonlink"})

            spaceUsed, spaceMax = parse_space(link['title'])
            coords = parse_coordinates((link(attrs={'class': "planet-koords"})[0].contents[0]).decode('utf-8'))
            pID = urlparse.parse_qs(link['href'])['cp'][0]

            planet = Planet(((link(attrs={'class': "planet-name"})[0].contents[0]).decode('utf-8')),
                          pID, spaceUsed, spaceMax, coords)
            planets.append(planet)

            if mlink is not None:
                name = mlink.find('img')['alt']
                mID = urlparse.parse_qs(mlink['href'])['cp'][0]
                spaceUsed, spaceMax = parse_space(mlink['title'])

                moon = Planet(name, mID, spaceUsed, spaceMax, coords)
                moon.isMoon = True
                moon.hasMoon = True

                planet.moon = moon
                planet.hasMoon = True
                planets.append(moon)



        return planets


def parse_coordinates(coords):
    return coords.replace('[', '').replace(']', '')

def parse_space(title):

    try:
        data = title.split('(')[1]
        data = data.split(')')[0]
        data = data.split('/')

        used, total = data[0], data[1]

        if 'overmark' in used:
            used = total

        used, total = int(used), int(total)

    # Default to 0
    except Exception:
        used, total = 0, 0

    return used, total

