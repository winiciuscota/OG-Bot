from scraper import Scraper

class missile(Scraper):
    """Handle usage of interplanetary missiles"""

    def launch_missile(self, coordinates, missiles_count = 10):
        "launch the number of missiles to the coordinates "
        url = self.url_provider.get_page_url("missile")
        galaxy = coordinates.split(':')[0]
        system = coordinates.split(':')[1]
        position = coordinates.split(':')[2]
        data = urllib.urlencode({'galaxy': galaxy, 'system': system, 'position': position, 'planetType': 1})
        self.open_url(url, data)
        self.browser.select_form(name='rocketForm')
        self.browser['anz'] = missiles_count
        self.submit_request()