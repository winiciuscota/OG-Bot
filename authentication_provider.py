import logging
from mechanize import Browser
from bs4 import BeautifulSoup
import cookielib
import os

class AuthenticationProvider:

    def __init__(self, username, password, universe):
        self.LoginUrl = 'http://br.ogame.gameforge.com/'
                        # http://s114-br.ogame.gameforge.com/game/index.php?page=overview
        self.IndexUrl = 'http://s%s-br.ogame.gameforge.com' % universe + '/game/index.php'
        self.Headers = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')]
        # Dados de autenticacao
        self.Username = username
        self.Password = password
        self.Universe = universe

        self.logger = logging.getLogger('ogame-bot')
        # Preparando o browser
        self.cj = cookielib.LWPCookieJar()

        self.br = Browser()
        self.br.set_cookiejar(self.cj)
        self.br.set_handle_robots(False)
        self.br.addheaders = self.Headers
        self.path = os.path.dirname(os.path.realpath(__file__))

    def verify_connection(self):
        res = self.br.open(self.IndexUrl)
        soup = BeautifulSoup(res.get_data())
        if soup.find("meta", { "name" : "ogame-player-name" }) == None:
            return False
        else:
            self.logger.info('Connection is ok')
            self.logger.info('Logged in as %s ' % soup.find("meta", { "name" : "ogame-player-name" })['content'])
            self.logger.info('Language is %s ' % soup.find("meta", { "name" : "ogame-language" })['content'])
            self.logger.info('Game version is %s ' % soup.find("meta", { "name" : "ogame-version" })['content'])
            return True

    def connect(self):
        self.logger.info('Opening login page ' + self.LoginUrl)
        # Open login page
        self.br.open(self.LoginUrl)
        self.br.select_form(name="loginForm")

        # enter Username and password
        self.br['login'] = self.Username
        self.br['pass'] = self.Password
        self.br['uni'] = ['s%s-br.ogame.gameforge.com' % self.Universe]
        self.logger.info('Logging in to server: %s' % self.br['uni']  )
        self.br.submit()
        self.logger.info(self.IndexUrl)
        self.logger.info('Saving authentication data')

    def get_browser(self):

        # name of the cookies file
        cookiesFileName = os.path.join(self.path, 'cookies.txt')

        # Check if cookies file exists
        if os.path.isfile(cookiesFileName):
            self.logger.info('Found stored cookies')
            self.cj.load(cookiesFileName)
            if self.verify_connection():
                return self.br
            else:
                self.logger.info('Could not restore session from cookies file')
        self.connect()
        self.verify_connection()

        self.cj.save(cookiesFileName)
        return self.br
