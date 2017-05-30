import ConfigParser
import logging
import os
import re


class Config(object):
    def __init__(self, args):
        config = ConfigParser.ConfigParser()

        parameters = vars(args)
        config_file = parameters.get('c')

        current_file = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(current_file, '../')
        os.chdir(path)

        if config_file is None:
            config_file = 'user.cfg'

        cfg = config.read(config_file)

        if len(cfg) == 0:
            print 'Error while parsing config file \'' + config_file + "'"
            exit()

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


        if not cfg:
            # Config file is empty, log error
            self.logger.error(self.WRONG_ARGUMENTS_MESSAGE)
            exit()

        else:
            # Set configuration from config file
            self.logger.info('Getting user info from config file %s', config_file)

            # User config options
            self.username = config.get('UserInfo', 'Username')
            self.password = config.get('UserInfo', 'Password')
            self.universe = config.get('UserInfo', 'Universe')
            self.country = config.get('UserInfo', 'Country')

            # General config options
            self.mode = self.parse_multiple_value_config(config.get('General', 'DefaultMode'))
            self.default_origin_planet_name = config.get('General', 'DefaultOriginPlanet')
            self.excluded_planets = map(lambda x: x.strip().lower(),
                                        config.get('General', 'ExcludedPlanets').split(','))
            self.log_level = config.get('General', 'LogLevel')  # Get loglevel

            # Development config options
            self.build_fusion_reactor = config.getboolean('Development', 'FusionReactor')  # build fusion reactor or not
            self.build_solar_plant = config.getboolean('Development', 'SolarPlant')  # build solar plant or not
            self.build_storage = config.getboolean('Development', 'Storage')  # build storage structures or not
            self.defense_proportion = self.parse_multiple_value_config(config.get('Development', 'DefenseProportion'))
            self.spend_excess_metal_on_rl = config.getboolean('Development', 'SpendExcessMetalOnRL')

            try:
                self.maxFields = config.getint('Development', 'MaxUsedFields')

            except Exception:
                self.maxFields = 150

            try:
                self.minFreeFields = config.getint('Development', 'MinFreeFields')

            except Exception:
                self.minFreeFields = 20

            # Transport config options
            self.transport_metal = config.getboolean('Transport', 'TransportMetal')
            self.transport_crystal = config.getboolean('Transport', 'TransportCrystal')
            self.transport_deuterium = config.getboolean('Transport', 'TransportDeuterium')

            # Exploration config options
            self.attack_range = config.getint('Exploration', 'AttackRange')
            self.time_to_wait_for_probes = config.getint('Exploration', 'HowLongToWaitForProbes')
            self.spy_report_life = config.getint('Exploration', 'SpyReportLife')  # Time in which spy report is valid
            self.minimum_inactive_target_rank = config.getint('Exploration', 'MinimumInactiveTargetRank')
            self.maximum_inactive_target_rank = config.getint('Exploration', 'MaximumInactiveTargetRank')
            self.spy_fleet_min_delay = config.getint('Exploration',
                                                     'SpyFleetMinDelay')  # Minimum time between sending next spy
            self.spy_fleet_max_delay = config.getint('Exploration',
                                                     'SpyFleetMaxDelay')  # maximum time between sending next spy
            self.attack_fleet_min_delay = config.getint('Exploration',
                                                        'AttackFleetMinDelay')  # Minimum time between sending next attack
            self.attack_fleet_max_delay = config.getint('Exploration',
                                                        'AttackFleetMaxDelay')  # Maximum time between sending next attack
            self.expedition_fleet_min_delay = config.getint('Exploration',
                                                            'ExpeditionFleetMinDelay')  # Minimum time between sending next expedition
            self.expedition_fleet_max_delay = config.getint('Exploration',
                                                            'ExpeditionFleetMaxDelay')  # Maximum time between sending next expedition
            self.spy_probes_count = config.getint('Exploration', 'SpyProbesCount')  # Amount of spy probes to send
            self.min_res_to_attack = config.getint('Exploration', 'MinResToSendAttack')  # Min resources to send attack
            self.expedition_range = config.getint('Exploration', 'ExpeditionRange')  # range to send expeditions

            self.enable_twilio_messaging = config.getboolean('Twilio', 'EnableTwilioMessaging')
            self.twilio_account_sid = config.get('Twilio', 'AccountSid')
            self.twilio_account_token = config.get('Twilio', 'AccountToken')
            self.twilio_from_number = config.get('Twilio', 'FromNumber')
            self.twilio_to_number = config.get('Twilio', 'ToNumber')

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

            #Scheduler configuration
            #self.schedules[print_resources = {}
            schedules = {}
            schedules['print_resources'] = {}
            schedules['print_resources']['enable'] = config.getboolean('Scheduler', 'PrintRessources' )
            schedules['print_resources']['delay'] = config.getint('Scheduler', 'PrintRessourcesDelay')
            schedules['auto_build_structures'] = {}
            schedules['auto_build_structures']['enable'] = config.getboolean('Scheduler', 'AutoBuildStructures' )
            schedules['auto_build_structures']['delay'] = config.getint('Scheduler', 'AutoBuildStructuresDelay')
            schedules['auto_research'] = {}
            schedules['auto_research']['enable'] = config.getboolean('Scheduler', 'AutoResearch' )
            schedules['auto_research']['delay'] = config.getint('Scheduler', 'AutoResearchDelay')
            schedules['attack_inactive_planets'] = {}
            schedules['attack_inactive_planets']['enable'] = config.getboolean('Scheduler', 'AttackInactivePlanets' )
            schedules['attack_inactive_planets']['delay'] = config.getint('Scheduler', 'AttackInactivePlanetsDelay')
            schedules['auto_build_defenses'] = {}
            schedules['auto_build_defenses']['enable'] = config.getboolean('Scheduler', 'AutoBuildDefenses' )
            schedules['auto_build_defenses']['delay'] = config.getint('Scheduler', 'AutoBuildDefensesDelay')
            schedules['transport_resources_to_weaker_planet'] = {}
            schedules['transport_resources_to_weaker_planet']['enable'] = config.getboolean('Scheduler', 'TransportResourcesToWeakerPlanet' )
            schedules['transport_resources_to_weaker_planet']['delay'] = config.getint('Scheduler', 'TransportResourcesToWeakerPlanetDelay')
            schedules['explore'] = {}
            schedules['explore']['enable'] = config.getboolean('Scheduler', 'Explore' )
            schedules['explore']['delay'] = config.getint('Scheduler', 'ExploreDelay')


            self.schedules = schedules

    @staticmethod
    def parse_multiple_value_config(str):
        """
        :param str: string to parse
        :return: parsed vector of arguments
        """
        multiple_value_config = re.split(',| ', str)

        return filter(lambda x: x is not "", multiple_value_config)
