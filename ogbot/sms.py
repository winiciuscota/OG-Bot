from twilio.rest import TwilioRestClient


class SMSSender:

    def __init__(self, config):
        self.config = config

    def send_sms(self, message):
        if self.config.enable_twilio_messaging:
           twilio_client = TwilioRestClient(self.config.twilio_account_sid, self.config.twilio_account_token)
           twilio_client.messages.create(to=self.config.twilio_to_number, from_=self.config.twilio_from_number,
                                         body=message)
