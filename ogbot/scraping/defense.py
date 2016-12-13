from bs4 import BeautifulSoup
import re
from scraper import *

DEFENSES_DATA = {

    "rl": DefenseItem(401, "Rocket Launcher"),
    "ll": DefenseItem(402, "Light Laser"),
    "hl": DefenseItem(403, "Heavy Laser"),
    "gc": DefenseItem(404, "Gauss Cannon"),
    "ic": DefenseItem(405, "Ion Cannon"),
    "pt": DefenseItem(406, "Plasma Turret"),
    "ssd": DefenseItem(407, "Small Shield Dome"),
    "lsd": DefenseItem(408, "Large Shield Dome"),
    "abm": DefenseItem(502, "Anti-Ballistic Missile"),
    "im": DefenseItem(503, "Interplanetary Missile"),

    "401": DefenseItem(401, "Rocket Launcher"),
    "402": DefenseItem(402, "Light Laser"),
    "403": DefenseItem(403, "Heavy Laser"),
    "404": DefenseItem(404, "Gauss Cannon"),
    "405": DefenseItem(405, "Ion Cannon"),
    "406": DefenseItem(406, "Plasma Turret"),
    "407": DefenseItem(407, "Small Shield Dome"),
    "408": DefenseItem(408, "Large Shield Dome"),
    "502": DefenseItem(502, "Anti-Ballistic Missile"),
    "503": DefenseItem(503, "Interplanetary Missile")
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
            id = def_button['ref']
            defense_data = DEFENSES_DATA.get(id)

            # ensures that execution will not break if there is a new item
            if defense_data is not None:
                amount = int(re.findall('\d+', def_button.text.strip())[0])
                item = DefenseItem(defense_data.id, defense_data.name)
                defenses.append(ItemAction(item, amount))

        return defenses

    def auto_build_defenses_to_planet(self, planet):
        """
        Automatically build defenses to the specified planet
        :param planet: planet to build defenses on
        :return:
        """

        defense_items = [ItemAction(DEFENSES_DATA.get(Defenses.PlasmaTurret), 20),
                         ItemAction(DEFENSES_DATA.get(Defenses.GaussCannon), 50),
                         ItemAction(DEFENSES_DATA.get(Defenses.IonCannon), 10),
                         ItemAction(DEFENSES_DATA.get(Defenses.HeavyLaser), 10),
                         ItemAction(DEFENSES_DATA.get(Defenses.LightLaser), 3000),
                         ItemAction(DEFENSES_DATA.get(Defenses.RocketLauncher), 3000)]

        self.logger.info('Auto building defenses')
        self.redirect_to_page(planet)
        for defense_item in defense_items:
            self.logger.info("building %d %s(s) on planet %s" % (defense_item.amount,
                                                                 defense_item.item.name,
                                                                 planet.name))
            self.build_defense_on_current_page(defense_item.item.id, defense_item.amount)

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
