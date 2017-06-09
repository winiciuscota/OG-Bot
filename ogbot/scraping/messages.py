#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from enum import Enum
import urllib
import galaxy
import general
import datetime
import traceback
from scraper import Scraper


class Messages(Scraper):
    def __init__(self, browser, config):
        super(Messages, self).__init__(browser, config)

    def get_messages(self):
        raise NotImplementedError

    def get_spy_reports(self):
        self.logger.info('Getting messages')
        url = self.url_provider.get_page_url('messages')
        data = urllib.urlencode({'tab': 20, 'ajax': 1})

        self.logger.info("Getting messages for first page")
        res = self.open_url(url, data)
        soup = BeautifulSoup(res.read(), "lxml")
        spy_reports = []

        # add messages from the first page
        spy_reports.extend(self.parse_spy_reports(soup))

        pagination_info = soup.find('li', {"class": "curPage"}).text
        page_count = int(pagination_info.split('/')[1])

        # add messages from the other pages
        for page in range(1, page_count):

            try:
                page_number = page + 1
                self.logger.info("Getting messages for page %d" % page_number)
                data = urllib.urlencode({'messageId': -1, 'tabid': 20, 'action': 107, 'pagination': page_number, 'ajax': 1})
                res = self.open_url(url, data)
                soup = BeautifulSoup(res.read(), "lxml")
                page_reports = self.parse_spy_reports(soup)
                spy_reports.extend(page_reports)

            except Exception as e:
                exception_message = traceback.format_exc()
                self.logger.error(exception_message)

        return spy_reports

    def clear_spy_reports(self):
        #return True
        url = self.url_provider.get_page_url('messages')
        data = urllib.urlencode({'tab': 20, 'messageId': -1, 'action': 103, 'ajax': 1})
        self.open_url(url, data)
        self.logger.info("Clearing spy reports")

    def parse_spy_reports(self, soup):
        """parse spy reports for an individual page"""
        message_boxes = soup.findAll("li", {"class": "msg "})
        message_boxes += soup.findAll("li", {"class": "msg msg_new"})
        spy_reports = []

        for message_box in message_boxes:

            try:

                # We already are in the espionage tab, there is only spy reports and reports from other
                # players spying on us here. If the report is from other player spying on us the message div
                # should contain an span with the class espionageDefText
                is_spy_report = True if message_box.find("span", {"class": "espionageDefText"}) is None else False

                msg_date_node = message_box.find("span", {"class": "msg_date fright"})
                message_datetime = parse_report_datetime(
                    msg_date_node.text if msg_date_node is not None else "1.1.2016 00:00:00")

                if is_spy_report:
                    planet_info = message_box.find("a", {"class": "txt_link"}).text
                    planet_name = planet_info.split('[')[0].strip()
                    coordinates_data = planet_info.split('[')

                    # If there is nothing after an '[' character it means the planet has been destroyed
                    if len(coordinates_data) <= 1:
                        self.logger.info("Hmm, I found a destroyed planet")
                        continue

                    coordinates = coordinates_data[1].replace(']', '').strip()
                    # find inactive player name
                    player_node = message_box.find("span", {"class": "status_abbr_longinactive"})

                    # If not long inactive, check for simply inactive
                    if player_node is None:
                        player_node = message_box.find("span", {"class": "status_abbr_inactive"})

                    if player_node is not None:
                        player_name = player_node.text.strip()
                        player_state = galaxy.PlayerState.Inactive

                    else:
                        # if the player isn't inactive I don't care about the name
                        player_name = 'unknown'
                        player_state = galaxy.PlayerState.Active

                    message_content = message_box.findAll("div", {"class": "compacting"})

                    if len(message_content) > 0:
                        resources_row = message_content[1]
                        resources_data = resources_row.findAll("span", {"class": "resspan"})
                        resources = None
                        if resources_data is not None:
                            metal = parse_resource(resources_data[0].text)
                            crystal = parse_resource(resources_data[1].text)
                            deuterium = parse_resource(resources_data[2].text)
                            resources = general.Resources(metal, crystal, deuterium)
                        loot_row = message_content[2]
                        loot_data = loot_row.find("span", {"class": "ctn ctn4"})
                        loot = parse_loot_percentage(loot_data.text)
                        defense_row = message_content[3]
                        fleet_data = defense_row.find("span", {"class": "ctn ctn4 tooltipLeft"})
                        defenses_data = defense_row.find("span", {"class": "ctn ctn4 fright tooltipRight"})

                        if fleet_data is not None and defenses_data is not None:
                            fleet = parse_resource(fleet_data.text)
                            defenses = parse_resource(defenses_data.text)
                        else:
                            fleet = None
                            defenses = None
                    else:
                        fleet = None
                        defenses = None
                        resources = None
                        loot = None

                    report = SpyReport(planet_name.encode('utf-8'), player_name, player_state, coordinates, resources, fleet,
                                       defenses, loot, message_datetime)
                    spy_reports.append(report)

            except Exception as e:
                exception_message = traceback.format_exc()
                self.logger.error(exception_message)

        return spy_reports


def parse_resource(text):
    """Use to parse resources values to int, ex: metal: 2.492M becomes 2492000"""

    try:
        value = int(text.split(':')[1].strip().replace(".", "").replace(",", "").replace("Mn", "000").replace("M", "000"))
    except Exception as e:
        print 'Failed to parse resources string "' + text + '"'
        exception_message = traceback.format_exc()
        self.logger.error(exception_message)

        # Default to 0
        value = 0

    return value


def parse_loot_percentage(text):
    """Use to parse loot percentage string, ie: Roubo: 50% becomes 0.5"""

    try:
        percentage = float(text.split(':')[1].strip("%")) / 100

    except Exception as e:
        print 'Failed to parse loot string "' + text + '"'
        exception_message = traceback.format_exc()
        self.logger.error(exception_message)

        # Default to 50 %
        percentage = 0.5

    return percentage


def parse_report_datetime(text):
    time = datetime.datetime.strptime(text.strip(), "%d.%m.%Y %H:%M:%S")
    return time


class MessageType(Enum):
    SpyReport = 1


class SpyReport(object):
    def __init__(self, planet_name, player_name, player_state, coordinates, resources, fleet, defenses, loot,
                 report_datetime):
        self.planet_name = planet_name
        self.player_name = player_name
        self.player_state = player_state
        self.coordinates = coordinates
        self.resources = resources
        self.defenses = defenses
        self.fleet = fleet
        self.loot = loot
        self.report_datetime = report_datetime

    def __str__(self):
        return "Planet %s,Player %s, State: %s, coordinates %s, Resouces = %s, Fleet: %s, Defenses: %s, Loot: %s " % (
        self.planet_name, self.player_name, self.player_state, self.coordinates, self.resources, self.fleet,
        self.defenses, self.loot)

    def get_loot(self):
        return self.resources.total() * self.loot
