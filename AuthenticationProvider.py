import logging
from mechanize import Browser
from Hangar import Hangar
import cookielib
import os

class AuthenticationProvider:

    def __init__(self, username, password, universe):
        self.BaseUrl = 'http://www.ogame.com.br/'
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

    def GetBrowser(self):
        self.logger.info('Opening Login page ' + self.BaseUrl)
        self.br.open(self.BaseUrl)
        self.br.select_form(name="loginForm")

        # enter Username and password
        self.br['login'] = self.Username
        self.br['pass'] = self.Password
        self.br['uni'] = ['s%s-br.ogame.gameforge.com' % self.Universe]

        self.logger.info('Logging in to server: %s' % self.br['uni']  )
        self.br.submit()

        self.logger.info('Saving authentication data')
        self.cj.save(os.path.join(self.path, 'cookies.txt'))
        return self.br
