import ConfigParser
import logging
import os


class Config(object):
    def __init__(self, args):
        config = ConfigParser.ConfigParser()

        current_file = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(current_file, '../')
        os.chdir(path)
        cfg = config.read('user.cfg')
        self.logger = logging.getLogger('OGBot')
        self.WRONG_ARGUMENTS_MESSAGE = """
            You must pass at least 3 arguments:
                You must have the following data on the user.cfg

                [UserInfo]
                username = your_username
                password = your_password
                universe = your_universe

                [Settings]
                DefaultMode = transport_resources_to_planet
                DefaultOriginPlanet = origin_planet_name
                AttackRange = 10
                HowLongToWaitForProbes = 60
                """

        parameters = vars(args)

        if not cfg:
            # Config file is empty, log error
            self.logger.error(self.WRONG_ARGUMENTS_MESSAGE)

            exit()
        else:
            # Set configuration from config file

            self.logger.info('Getting user info from config file')
            self.username = config.get('UserInfo', 'Username')
            self.password = config.get('UserInfo', 'Password')
            self.universe = config.get('UserInfo', 'Universe')
            self.country = config.get('UserInfo', 'Country')
            self.mode = []
            for dmode in config.get('Settings', 'DefaultMode').split(','):
                self.mode.append(dmode.strip())
            self.default_origin_planet_name = config.get('Settings', 'DefaultOriginPlanet')
            self.attack_range = config.getint('Settings', 'AttackRange')
            self.time_to_wait_for_probes = config.getint('Settings', 'HowLongToWaitForProbes')
            self.spy_report_life = config.getint('Settings', 'SpyReportLife')  # Time in which spy report is valid
            self.minimum_inactive_target_rank = config.getint('Settings', 'MinimumInactiveTargetRank')
            self.maximum_inactive_target_rank = config.getint('Settings', 'MaximumInactiveTargetRank')
            self.spy_fleet_min_delay = config.getint('Settings',
                                                     'SpyFleetMinDelay')  # Minimum time between sending next spy
            self.spy_fleet_max_delay = config.getint('Settings',
                                                     'SpyFleetMaxDelay')  # maximum time between sending next spy
            self.attack_fleet_min_delay = config.getint('Settings',
                                                        'AttackFleetMinDelay')  # Minimum time between sending next attack
            self.attack_fleet_max_delay = config.getint('Settings',
                                                        'AttackFleetMaxDelay')  # Maximum time between sending next attack
            self.expedition_fleet_min_delay = config.getint('Settings',
                                                            'ExpeditionFleetMinDelay')  # Minimum time between sending next expedition
            self.expedition_fleet_max_delay = config.getint('Settings',
                                                            'ExpeditionFleetMaxDelay')  # Maximum time between sending next expedition
            self.spy_probes_count = config.getint('Settings', 'SpyProbesCount')  # Amount of spy probes to send
            self.min_res_to_attack = config.getint('Settings', 'MinResToSendAttack')  # Min resources to send attack
            self.expedition_range = config.getint('Settings', 'ExpeditionRange')  # range to send expeditions
            self.build_fusion_reactor = config.getboolean('Settings', 'FusionReactor') # build fusion reactor or not
            self.build_solar_plant = config.getboolean('Settings', 'SolarPlant') # build solar planet or not

            # read values from parameters
            mode = parameters.get('m')
            attack_range = parameters.get('r')
            planet_name = parameters.get('p')
            self.scheduler = parameters.get('s')

            # Override default mode if the user has specified a mode by parameters
            if mode is not None:
                self.mode = mode

            if attack_range is not None:
                self.attack_range = int(attack_range)

            self.planet_name = planet_name
