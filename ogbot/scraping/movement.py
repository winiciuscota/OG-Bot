from bs4 import BeautifulSoup
from datetime import datetime
from scraper import *
from general import General


def get_arrival_time(arrival_time_str):
    time = datetime.strptime(arrival_time_str.strip(), '%H:%M:%S').time()
    now = datetime.now()
    arrival_time = datetime.combine(now, time)
    return arrival_time


class Movement(Scraper):
    def __init__(self, browser, config):
        super(Movement, self).__init__(browser, config)
        self.general_client = General(browser, config)

    def get_fleet_movement_from_movement_page(self):
        """
        Deprecated, use get_fleet_movement instead
        :return:
        """
        url = self.url_provider.get_page_url('movement')
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        movement_nodes = soup.findAll("div", {"class": "fleetDetails detailsOpened"})
        fleet_movements = []
        for movement_node in movement_nodes:
            origin_planet_coords = self.parse_coords(movement_node.find("span", {"class": "originCoords"}).text)
            origin_planet_name = movement_node.find("span", {"class": "originPlanet"}).text.strip()
            destination_coords = self.parse_coords(
                movement_node.find("span", {"class": "destinationCoords tooltip"}).text)
            movement = FleetMovement(origin_planet_coords, origin_planet_name, destination_coords)
            fleet_movements.append(movement)
        return fleet_movements

    def get_fleet_movement(self):
        url = self.url_provider.get_page_url('eventList')
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")

        movement_table = soup.find("table", {"id": "eventContent"})
        movement_rows = movement_table.findAll("tr", {"class": "eventFleet"})

        fleet_movements = []
        for movement_row in movement_rows:
            origin_coords = self.parse_coords(movement_row.find("td", {"class": "coordsOrigin"}).text.strip())
            origin_planet_name = movement_row.find("td", {"class": "originFleet"}).text.strip()
            dest_coords = self.parse_coords(movement_row.find("td", {"class": "destCoords"}).text.strip())
            dest_planet_name = movement_row.find("td", {"class": "destFleet"}).text.strip()
            count_down_td = movement_row.find("td", {"class": "countDown"})
            is_friendly = 'friendly' in count_down_td.attrs['class']

            arrival_time_str = movement_row.find("td", {"class": "arrivalTime"}).text
            arrival_time = get_arrival_time(arrival_time_str)
            countdown_time = self.get_countdown_time(arrival_time)

            movement = FleetMovement(origin_coords, origin_planet_name, dest_coords, dest_planet_name, is_friendly,
                                     arrival_time, countdown_time)
            fleet_movements.append(movement)

        return fleet_movements

    def get_countdown_time(self, arrival_time):
        game_time = self.general_client.get_game_datetime()
        return arrival_time - game_time

    @staticmethod
    def parse_coords(text):
        return text.replace('[', '').replace(']', '')

    def get_fleet_slots_usage(self):
        """
            Get fleet slot usage data. Only works if there is at least 1 fleet in movement
        """
        url = self.url_provider.get_page_url('movement')
        res = self.open_url(url)
        soup = BeautifulSoup(res.read())
        slots_info_node = soup.find("span", {"class", "fleetSlots"})
        if slots_info_node is not None:
            current_slots = int(slots_info_node.find("span", {"class", "current"}).text)
            all_slots = int(slots_info_node.find("span", {"class", "all"}).text)
        else:
            current_slots = 0
            all_slots = 1
        return current_slots, all_slots
