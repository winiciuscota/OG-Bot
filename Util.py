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

    def GetPageUrl(self, page, planet = None):
        url = self.PAGES[page]
        if planet is not None:
            url += '&cp=%s' % planet.id
        return url

    def GetMainUrl(self):
        return self.MAIN_URL

def sanitize(t):
    for i in t:
        try:
            yield int(i)
        except ValueError:
            yield i
