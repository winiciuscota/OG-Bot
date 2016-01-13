#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
from enum import Enum
import urllib
import galaxy
import general


class Messages:

    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser
        self.spy_report_title = u'Relatório de espionagem'

    def get_messages(self):
        raise NotImplementedError

    def get_spy_reports(self):
        self.logger.info('Getting messages')
        url = self.url_provider.get_page_url('messages')
        data = urllib.urlencode({'tab': 20, 'ajax' : 1})

        self.logger.info("Getting messages for first page")
        res = self.browser.open(url, data=data)
        soup = BeautifulSoup(res.read())
        spy_reports = []

        # add messages from the first page
        spy_reports.extend(self.parse_spy_reports(soup))

        pagination_info = soup.find('li', {"class" : "curPage"}).text

        page_count = int(pagination_info.split('/')[1])

        # add messages from the other pages
        for page in range(1, page_count):
            page_number = page + 1
            self.logger.info("Getting messages for page %d" % page_number)
            data = urllib.urlencode({'messageId' : -1, 'tabid': 20, 'action' : 107, 'pagination' : page_number, 'ajax' : 1})
            res = self.browser.open(url, data=data)
            soup = BeautifulSoup(res.read())
            spy_reports.extend(self.parse_spy_reports(soup))
        return spy_reports


    def parse_spy_reports(self, soup):
        message_boxes = soup.findAll("li", { "class" : "msg " })
        spy_reports = []
        for message_box in message_boxes:
            message_title = unicode(message_box.find("span", {"class":"msg_title blue_txt"}).text)
            if self.spy_report_title in message_title:
                planet_info = message_box.find("a", {"class":"txt_link"}).text
                planet_name = planet_info.split('[')[0].strip()
                coordinates = planet_info.split('[')[1].replace(']','').strip()
                player_name = ''
                player_state = ''
                # find inactive player name
                player_node = message_box.find("span", {"class":"status_abbr_longinactive"})
                if player_node != None:
                    player_name = player_node.text.strip()
                    player_state = galaxy.PlayerState.Inactive
                else:
                    #if the player isn't inactive i don't care about the name
                    player_name = 'unknown'
                    player_state = galaxy.PlayerState.Active
                message_content = message_box.findAll("div", {"class": "compacting"})

                resources_row = message_content[1]
                resources_data = resources_row.findAll("span", {"class": "resspan"})
                resources = None
                if resources_data != None:
                    metal = self.parse_integer(resources_data[0].text)
                    crystal = self.parse_integer(resources_data[1].text)
                    deuterium = self.parse_integer(resources_data[2].text)
                    resources = general.Resources(metal, crystal, deuterium)

                defense_row = message_content[3]
                fleet_data = defense_row.find("span", {"class": "ctn ctn4 tooltipLeft"})
                defenses_data = defense_row.find("span", {"class": "ctn ctn4 fright tooltipRight"})

                if fleet_data != None and defenses_data != None:
                    fleet = self.parse_integer(fleet_data.text)
                    defenses = self.parse_integer(defenses_data.text)
                else:
                    fleet = None
                    defenses = None

                spy_reports.append(SpyReport(str(planet_name), player_name, player_state, str(coordinates), resources, fleet, defenses))

        return spy_reports

    def parse_integer(self, text):
        """Use to parse string values to int, ex: 2.492M becomes 2492000"""
        value = int(text.split(':')[1].strip().replace(".", "").replace("M", "000"))
        return value


class MessageType(Enum):
    SpyReport = 1

class SpyReport(object):
    def __init__(self, planet_name, player_name, player_state, coordinates, resources, defenses, fleet):
        self.planet_name = planet_name
        self.player_name = player_name
        self.player_state = player_state
        self.coordinates = coordinates
        self.resources = resources
        self.defenses = defenses
        self.fleet = fleet

    def __str__(self):
        return "Planet %s,Player %s, State: %s, coordinates %s, Resouces = %s, Fleet: %s, Defenses: %s, " % (self.planet_name, self.player_name, self.player_state, self.coordinates, self.resources, self.fleet, self.defenses)
