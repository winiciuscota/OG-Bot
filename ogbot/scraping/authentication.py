import logging
from mechanize import Browser
from bs4 import BeautifulSoup
import cookielib
import os
from scraper import Scraper


class AuthenticationProvider(Scraper):
    def __init__(self, config):
        self.login_url = 'http://%s.ogame.gameforge.com/' % config.country
        # http://s114-br.ogame.gameforge.com/game/index.php?page=overview
        self.index_url = 'http://s%s-%s.ogame.gameforge.com' % (config.universe, config.country) + '/game/index.php'
        headers = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')]
        # Authentication data
        self.username = config.username
        self.password = config.password
        self.universe = config.universe
        self.country = config.country

        self.logger = logging.getLogger('ogame-bot')
        # Setting up the browser
        self.cj = cookielib.LWPCookieJar()

        br = Browser()
        br.set_cookiejar(self.cj)
        br.set_handle_robots(False)
        br.addheaders = headers
        # self.path = os.path.dirname(os.path.realpath(__file__))
        # name of the cookies file
        # self.cookies_file_name = os.path.join(self.path, 'cookies.tmp')
        self.cookies_file_name = 'cookies.tmp'
        super(AuthenticationProvider, self).__init__(br, config)

    def verify_connection(self):
        res = self.open_url(self.index_url)
        soup = BeautifulSoup(res.get_data(), "lxml")
        if soup.find("meta", {"name": "ogame-player-name"}) is None:
            return False
        else:
            self.logger.info('Connection is ok')
            self.logger.info('Logged in as %s ' % soup.find("meta", {"name": "ogame-player-name"})['content'])
            self.logger.info('Language is %s ' % soup.find("meta", {"name": "ogame-language"})['content'])
            self.logger.info('Game version is %s ' % soup.find("meta", {"name": "ogame-version"})['content'])
            return True

    def connect(self):
        self.logger.info('Opening login page ' + self.login_url)
        # Open login page
        self.open_url(self.login_url)
        self.browser.select_form(name="loginForm")

        # Enter Username and password
        self.browser['login'] = self.username
        self.browser['pass'] = self.password
        self.browser['uni'] = ['s%s-%s.ogame.gameforge.com' % (self.universe, self.country)]
        self.logger.info('Logging in to server: %s' % self.browser['uni'])
        self.submit_request()
        self.logger.info('Saving authentication data')
        self.cj.save(self.cookies_file_name)

    def get_browser(self):
        # Check if cookies file exists
        if os.path.isfile(self.cookies_file_name):
            self.logger.info('Found stored cookies')
            self.cj.load(self.cookies_file_name, ignore_discard=True)
            if self.verify_connection():
                return self.browser
            else:
                self.logger.info('Could not restore session from cookies file')

        self.connect()
        connection = self.verify_connection()

        if not connection:
            self.logger.error("Unable to connect, check your username and password")
            exit()

        self.cj.save(self.cookies_file_name, ignore_discard=True)
        return self.browser
