from base import BaseBot

from scraping import research, general


class ResearcherBot(BaseBot):

    def __init__(self, browser, config, planets):
        self.research_client = research.Research(browser, config)
        self.general_client = general.General(browser, config)
        self.planets = planets
        super(ResearcherBot, self).__init__(browser, config, planets)

    def get_planet_for_research(self, planets=None):
        if planets is None:
            planets = self.planets

        #for now the main planet will be used for research
        return planets[0]

    def get_next_research_item(self, planet):
        available_research = self.research_client.get_available_research_for_planet(planet)
        available_research_item = None

        priority_list = [
            109,    #WeaponTech
            110,    #ShieldTech
            111,    #ArmourTech
            106,    #EspionageTech
            108,    #ComputerTech
            113,    #EnergyTech
            120,    #LaserTech
            115,    #CombustionDrive
            121,    #IonTech
            117,    #ImpulseDrive
            124,    #AstroPhysics
            114,    #HyperspaceTech
            118,    #HyperspaceDrive

        ]

        if available_research:
            for aresearch in available_research:
                if aresearch.id in priority_list:
                    available_research_item = aresearch
                    break

            if len(available_research) > 1:
                for research_canidate in available_research:
                    if research_canidate.id in priority_list:
                        rc_priority = priority_list.index(research_canidate.id)
                        r_priority =  priority_list.index(available_research_item.id)
                        if rc_priority < r_priority:
                            available_research_item = research_canidate


                self.logger.info("Available Research:")
                for item in available_research:
                    self.logger.info("      " + item.name)

        return available_research_item

    def auto_research_next_item(self):
        #planet = self.get_planet_for_research(self.planets)

        # Attempt research on each planet until one is started
        for planet in self.planets:

            try:
                research = self.get_next_research_item(planet)

                if research is not None:
                    self.research_client.research_item(research, planet)
                    break;

                else:
                    self.logger.info("Nothing to research on planet %s" % planet)

            except Exception as e:
                print e
                pass
