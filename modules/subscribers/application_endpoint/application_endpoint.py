__author__ = 'tinglev'

from modules import environment, deployment_util
from modules.subscribers.slack import slack_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    call_slack_channel_with_application_endpoint_url(deployment)
        
def call_slack_channel_with_application_endpoint_url(deployment):
    message = (f':information_source: About *{deployment_util.get_friendly_name(deployment)}* '
               f'https://app.kth.se/pipeline/#{deployment_util.get_application_name(deployment)}')

    for channel in deployment_util.get_slack_channels(deployment):
        slack_util.call_slack_endpoint(channel,
                                       environment.get_env(environment.SLACK_WEB_HOOK),
                                       create_slack_payload(message, channel))


def create_slack_payload(message, channel):
    return {
        'username': 'Alvares',
        'text': message,
        'icon_emoji': ':azure:',
        'channel': channel
    }
