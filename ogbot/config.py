import ConfigParser
import logging


class Config(object):

    #todo update message


    def __init__(self, argv):
        self.argv = argv
        config = ConfigParser.ConfigParser()
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
        if cfg == []:
            self.logger.error(self.WRONG_ARGUMENTS_MESSAGE)
            #Config file is empty, log an error

            exit()
        else:
            #Set configuration from config file

            self.logger.info('Getting user info from config file')
            self.username = config.get('UserInfo', 'Username')
            self.password = config.get('UserInfo', 'Password')
            self.universe = config.get('UserInfo', 'Universe')
            self.mode = config.get('Settings', 'DefaultMode')
            self.default_origin_planet_name = config.get('Settings', 'DefaultOriginPlanet')
            self.attack_range = config.getint('Settings', 'AttackRange')
            self.time_to_wait_for_probes = config.getint('Settings', 'HowLongToWaitForProbes')
            self.spy_report_life = config.getint('Settings', 'SpyReportLife') #Time in which spy report is valid
            self.minimun_inactive_target_rank = config.getint('Settings', 'MinimunInactiveTargetRank')
            self.maximun_inactive_target_rank = config.getint('Settings', 'MaximunInactiveTargetRank')
            self.spy_fleet_min_delay = config.getint('Settings', 'SpyFleetMinDelay') #Minimum time between sending next spy
            self.spy_fleet_max_delay = config.getint('Settings', 'SpyFleetMaxDelay') #maximum time between sending next spy
            self.attack_fleet_min_delay = config.getint('Settings', 'AttackFleetMinDelay') #Minimum time between sending next attack
            self.attack_fleet_max_delay = config.getint('Settings', 'AttackFleetMaxDelay') #Maximum time between sending next attack
            self.expedition_fleet_min_delay = config.getint('Settings', 'ExpeditionFleetMinDelay') #Minimum time between sending next expedition
            self.expedition_fleet_max_delay = config.getint('Settings', 'ExpeditionFleetMaxDelay') #Maximum time between sending next expedition
            self.spy_probes_count = config.getint('Settings', 'SpyProbesCount') # Amount of spy probes to send
            self.min_res_to_attack = config.getint('Settings', 'MinResToSendAttack') #Min resources to send attack
            self.expedition_range = config.getint('Settings', 'ExpeditionRange') #range to send expeditions

            #Override default mode if the user has specified a mode by parameters
            if len(self.argv) > 1 :
               self.mode =self.argv[1]

            #Planet to operate in
            self.planet_name = self.argv[2] if len(self.argv) > 2 else None
