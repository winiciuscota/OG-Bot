import logging
from mechanize import Browser
from bs4 import BeautifulSoup
import cookielib
import os
from scraper import Scraper
import urllib2


class AuthenticationProvider(Scraper):
    def __init__(self, config):
        self.login_url = 'http://%s.ogame.gameforge.com/' % config.country
        self.server_url = 'http://s%s-%s.ogame.gameforge.com' % (config.universe, config.country)
        self.index_url = self.server_url + '/game/index.php'
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

        self.parseServerConfig(br, config)

        cookies_dir = 'cookies/'

        if not os.path.isdir(cookies_dir):
            os.mkdir(cookies_dir)

        cookies_id = self.country + '-' + self.universe + '-' + self.username

        self.cookies_file_name = cookies_dir + cookies_id + '.tmp'
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

            try:
                rank = soup.find("div", {"id": "bar"}).findAll('li')[1].text
                rank = rank.split('(')[1]
                rank = rank.split(')')[0]

            # Default to 0
            except Exception:
                rank = '??'

            self.logger.info('Current rank : %s' % rank)

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

    def parseServerConfig(self, browser, config):

        server = Server()
        config.server = server

        try:
            resp = urllib2.urlopen(self.server_url + '/api/serverData.xml')

            soup = BeautifulSoup(resp.read(), "xml")

            server.name = soup.find("name").string
            server.timezone = soup.find("timezone").string
            server.timezoneOffset = soup.find("timezoneOffset").string
            server.version = soup.find("version").string
            server.speed = int(soup.find("speed").string)
            server.speedFleet = int(soup.find("speedFleet").string)
            server.galaxies = int(soup.find("galaxies").string)
            server.systems = int(soup.find("systems").string)
            server.acs = bool(int(soup.find("acs").string))
            server.rapidFire = bool(int(soup.find("rapidFire").string))
            server.defToTF = bool(int(soup.find("defToTF").string))
            server.debrisFactor = float(soup.find("debrisFactor").string)
            server.debrisFactorDef = float(soup.find("debrisFactorDef").string)
            server.repairFactor = float(soup.find("repairFactor").string)
            server.newbieProtectionLimit = int(soup.find("newbieProtectionLimit").string)
            server.newbieProtectionHigh = int(soup.find("newbieProtectionHigh").string)
            server.topScore = int(soup.find("topScore").string)
            server.bonusFields = int(soup.find("bonusFields").string)
            server.donutGalaxy = bool(int(soup.find("donutGalaxy").string))
            server.donutSystem = bool(int(soup.find("donutSystem").string))
            server.wfEnabled = bool(int(soup.find("wfEnabled").string))
            server.wfMinimumRessLost = int(soup.find("wfMinimumRessLost").string)
            server.wfMinimumLossPercentage = int(soup.find("wfMinimumLossPercentage").string)
            server.wfBasicPercentageRepairable = int(soup.find("wfBasicPercentageRepairable").string)
            server.globalDeuteriumSaveFactor = float(soup.find("globalDeuteriumSaveFactor").string)

        except Exception:
            server.debrisFactor = 0.3
            server.systems = 499
            server.galaxies = 7

        print vars(server)

class Server():
    pass
