import logging
from mechanize import Browser
from bs4 import BeautifulSoup
import cookielib
import os

class AuthenticationProvider:

    def __init__(self, username, password, universe):
        self.login_url = 'http://br.ogame.gameforge.com/'
                        # http://s114-br.ogame.gameforge.com/game/index.php?page=overview
        self.index_url = 'http://s%s-br.ogame.gameforge.com' % universe + '/game/index.php'
        headers = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')]
        # Dados de autenticacao
        self.username = username
        self.password = password
        self.universe = universe

        self.logger = logging.getLogger('ogame-bot')
        # Preparando o browser
        self.cj = cookielib.LWPCookieJar()

        self.br = Browser()
        self.br.set_cookiejar(self.cj)
        self.br.set_handle_robots(False)
        self.br.addheaders = headers
        # self.path = os.path.dirname(os.path.realpath(__file__))
        # name of the cookies file
        # self.cookies_file_name = os.path.join(self.path, 'cookies.tmp')
        self.cookies_file_name = 'cookies.tmp'

    def verify_connection(self):
        res = self.br.open(self.index_url)
        soup = BeautifulSoup(res.get_data(), "lxml")
        if soup.find("meta", { "name" : "ogame-player-name" }) == None:
            return False
        else:
            self.logger.info('Connection is ok')
            self.logger.info('Logged in as %s ' % soup.find("meta", { "name" : "ogame-player-name" })['content'])
            self.logger.info('Language is %s ' % soup.find("meta", { "name" : "ogame-language" })['content'])
            self.logger.info('Game version is %s ' % soup.find("meta", { "name" : "ogame-version" })['content'])
            return True

    def connect(self):
        self.logger.info('Opening login page ' + self.login_url)
        # Open login page
        self.br.open(self.login_url)
        self.br.select_form(name="loginForm")

        # enter Username and password
        self.br['login'] = self.username
        self.br['pass'] = self.password
        self.br['uni'] = ['s%s-br.ogame.gameforge.com' % self.universe]
        self.logger.info('Logging in to server: %s' % self.br['uni']  )
        self.br.submit()
        self.logger.info('Saving authentication data')
        self.cj.save(self.cookies_file_name)

    def get_browser(self):
        # Check if cookies file exists
        if os.path.isfile(self.cookies_file_name):
            self.logger.info('Found stored cookies')
            self.cj.load(self.cookies_file_name, ignore_discard=True)
            if self.verify_connection():
                return self.br
            else:
                self.logger.info('Could not restore session from cookies file')
        self.connect()
        self.verify_connection()
        self.cj.save(self.cookies_file_name, ignore_discard=True)
        return self.br
