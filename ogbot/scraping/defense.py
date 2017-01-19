from bs4 import BeautifulSoup
import re
from scraper import *


ROCKET_LAUNCHER = DefenseItem(401, "Rocket Launcher", Resources(2000, 0))
LIGHT_LASER = DefenseItem(402, "Light Laser", Resources(1500, 500))
HEAVY_LASER = DefenseItem(403, "Heavy Laser", Resources(6000, 2000))
GAUSS_CANNON = DefenseItem(404, "Gauss Cannon", Resources(20000, 15000, 2000))
ION_CANNON = DefenseItem(405, "Ion Cannon", Resources(2000, 6000))
PLASMA_TURRET = DefenseItem(406, "Plasma Turret", Resources(50000, 50000, 30000))
SMALL_SHIELD_DOME = DefenseItem(407, "Small Shield Dome", Resources(10000, 10000))
LARGE_SHIELD_DOME = DefenseItem(408, "Large Shield Dome", Resources(50000, 50000))
ANTI_BALLISTIC_MISSILE = DefenseItem(502, "Anti-Ballistic Missile", Resources(8000, 2000))
INTERPLANETARY_MISSILE = DefenseItem(503, "Interplanetary Missile", Resources(12500, 2500, 10000))

DEFENSES_DATA = {

    "rl": ROCKET_LAUNCHER,
    "ll": LIGHT_LASER,
    "hl": HEAVY_LASER,
    "gc": GAUSS_CANNON,
    "ic": ION_CANNON,
    "pt": PLASMA_TURRET,
    "ssd": SMALL_SHIELD_DOME,
    "lsd": LARGE_SHIELD_DOME,
    "abm": ANTI_BALLISTIC_MISSILE,
    "im": INTERPLANETARY_MISSILE,

    "401": ROCKET_LAUNCHER,
    "402": LIGHT_LASER,
    "403": HEAVY_LASER,
    "404": GAUSS_CANNON,
    "405": ION_CANNON,
    "406": PLASMA_TURRET,
    "407": SMALL_SHIELD_DOME,
    "408": LARGE_SHIELD_DOME,
    "502": ANTI_BALLISTIC_MISSILE,
    "503": INTERPLANETARY_MISSILE
}


class Defenses:
    RocketLauncher = "rl"
    LightLaser = "ll"
    HeavyLaser = "hl"
    GaussCannon = "gc"
    IonCannon = "ic"
    PlasmaTurret = "pt"


class Defense(Scraper):
    def get_defenses(self, planet=None):
        """
        Get defenses for the given planet
        """
        self.logger.info('Getting defense data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('defense', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        defense_buttons = soup(attrs={'class': "detail_button"})

        defenses = []
        for def_button in defense_buttons:
            def_id = def_button['ref']
            defense_data = DEFENSES_DATA.get(def_id)

            # ensures that execution will not break if there is a new item
            if defense_data is not None:
                amount_level_text = def_button.find("span", {"class": "level"}).text
                amount = int(re.findall('\d+\.?\d*', amount_level_text)[0].replace(".", ""))

                item = DefenseItem(defense_data.id, defense_data.name)
                defenses.append(ItemAction(item, amount))

        return defenses

    def build_defense_to_planet(self, defense_type, amount, planet):
        """
        Build defense on specified planet
        :param defense_type: object of the defense type to build(must be of type DefenseItem)
        :param amount: amount of defenses to build
        :param planet: planet to build the defense on
        :return:
        """

        if self.url_provider.get_page_url("defense", planet) != self.get_current_url():
            self.logger.warning(self.url_provider.get_page_url("defense", planet))
            self.logger.warning(self.get_current_url())
            self.redirect_to_page(planet)
        try:
            self.logger.info("building %d %s(s) on planet %s" % (amount,
                                                                 defense_type.name,
                                                                 planet.name))

            self.build_defense_on_current_page(defense_type.id, amount)
        except Exception as e:
            self.logger.info('Error building defense')
            self.logger.info(e)

    def redirect_to_page(self, planet=None):
        """
        Redirect to defense page for the specified planet
        :param planet: Planet to redirect
        """

        url = self.url_provider.get_page_url('defense', planet)
        self.logger.info("Redirecting to page %s" % url)
        self.open_url(url)

    def build_defense_on_current_page(self, defense_id, amount):
        """
        Request building of defense type on current page,
        use it if you know that the bot is in the defense page
        for the right planet to save get requests
        :param defense_id: ID of the defense type to build
        :param amount: amount of defenses to build
        """

        self.logger.info("Writing data to form")
        self.create_control("form", "text", "menge", str(amount))
        self.create_control("form", "text", "type", str(defense_id))
        self.create_control("form", "text", "modus", "1")
        self.logger.info("Submitting build defense request")
        self.submit_request()

