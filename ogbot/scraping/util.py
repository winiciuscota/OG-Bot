import logging


class UrlProvider:
    def __init__(self, universe, country):
        self.main_url = 'https://s' + str(universe) + '-' + country + '.ogame.gameforge.com/game/index.php'
        self.logger = logging.getLogger('ogame-bot')

        self.pages = {
            'overview': self.main_url + '?page=overview',
            'resources': self.main_url + '?page=resources',
            'research': self.main_url + '?page=research',
            'shipyard': self.main_url + '?page=shipyard',
            'defense': self.main_url + '?page=defense',
            'fleet': self.main_url + '?page=fleet1',
            'galaxy': self.main_url + '?page=galaxy',
            'galaxyContent': self.main_url + '?page=galaxyContent',
            'messages': self.main_url + '?page=messages',
            'movement': self.main_url + '?page=movement',
            'missileAtack': self.main_url + '?page=missileattacklayer'
        }

    def get_pages(self):
        """
        Returns list of pages
        """
        return self.pages

    def get_page_url(self, page, planet=None):
        """
        Get page url for planet
        """
        url = self.pages.get(page)
        if planet is not None:
            url += '&cp=%s' % planet.link
        return url

    def get_main_url(self):
        """
        Return the main url
        """
        return self.main_url
