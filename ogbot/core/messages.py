from base import BaseBot
from datetime import timedelta

from scraping import messages, general, scraper


class MessagesBot(BaseBot):
    """Logging functions for the bot"""

    def __init__(self, browser, config, planets):
        self.messages_client = messages.Messages(browser, config)
        self.general_client = general.General(browser, config)

        super(MessagesBot, self).__init__(browser, config, planets)

    def clear_spy_reports(self):
        self.messages_client.clear_spy_reports()

    def get_spy_reports(self):
        """Get spy reports from the messages"""
        spy_reports = set(self.messages_client.get_spy_reports())
        return spy_reports

    def get_valid_spy_reports(self):
        game_date = self.general_client.get_game_datetime()

        reports = self.get_spy_reports()
        valid_reports = [report for report
                         in reports
                         # Get reports from inactive players only
                         if report.player_state == scraper.PlayerState.Inactive
                         # Get reports from last n minutes
                         and report.report_datetime >= (game_date - timedelta(minutes=self.config.spy_report_life))
                         ]

        return valid_reports

    def get_valid_spy_reports_from_inactive_targets(self):
        reports = self.get_valid_spy_reports()

        inactive_planets_reports = [report for report
                                    in reports
                                    # Get reports from inactive players only
                                    if report.player_state == scraper.PlayerState.Inactive
                                    ]

        return inactive_planets_reports
