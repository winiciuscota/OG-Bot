
class UrlProvider:
    def __init__(self, universe):
        self.MAIN_URL = 'http://s' + str(universe) + '-br.ogame.gameforge.com/game/index.php'

        self.PAGES = {
            'main':         self.MAIN_URL + '?page=overview',
            'resources':    self.MAIN_URL + '?page=resources',
            'station':      self.MAIN_URL + '?page=station',
            'research':     self.MAIN_URL + '?page=research',
            'shipyard':     self.MAIN_URL + '?page=shipyard',
            'defense':      self.MAIN_URL + '?page=defense',
            'fleet':        self.MAIN_URL + '?page=fleet1',
            'galaxy':       self.MAIN_URL + '?page=galaxy',
            'galaxyCnt':    self.MAIN_URL + '?page=galaxyContent',
            'events':       self.MAIN_URL + '?page=eventList'
        }

    def GetPages(self):
        return self.PAGES

    def GetPageUrl(self, page):
        return self.PAGES.get(page, None)

    def GetMainUrl(self):
        return self.MAIN_URL
