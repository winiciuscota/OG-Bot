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

        if available_research is not None:
            available_research_item = available_research[0]

            self.logger.info("Available Research:")
            for item in available_research:
                self.logger.info("      " + item.name)

            # Favor ship upgrades
            for item in available_research:
                if item.id in [109, 110, 111]:
                    available_research_item = item
                    break

        return available_research_item

    def auto_research_next_item(self):
        planet = self.get_planet_for_research(self.planets)
        research = self.get_next_research_item(planet)
        if research is not None:
            self.research_client.research_item(research, planet)
        else:
            self.logger.info("Nothing to research on planet %s" % planet)
