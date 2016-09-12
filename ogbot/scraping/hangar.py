import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
from scraper import *


class Hangar(Scraper):
    def get_ships(self, planet):
        self.logger.info('Getting shipyard data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('shipyard', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        ship_buttons = soup(attrs={'class': "detail_button"})

        ships = []
        for ship_button in ship_buttons:
            id = ship_button['ref']
            ship_data = self.SHIPS_DATA.get(id)

            # ensures that execution will not break if there is a new item
            if ship_data != None:

                try:
                    amount_info = "".join(ship_button.find("span", {"class": "level"})
                                          .findAll(text=True, recursive=False)[1])
                except IndexError:
                    amount_info = "".join(ship_button.find("span", {"class": "level"})
                                          .findAll(text=True, recursive=False)[0])
                amount = int(re.sub("[^0-9]", "", amount_info))
                ships.append(ItemAction(ShipItem(ship_data.id, ship_data.name), amount))

        return ships
