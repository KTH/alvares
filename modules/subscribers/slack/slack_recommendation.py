__author__ = 'tinglev@kth.se'

import logging
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import environment
from modules.subscribers.slack import slack_util

def subscribe():
    logger = logging.getLogger(__name__)
    logger.info('Adding Slack Recommendations as a subscriber.')
    subscribe_to_event('recommendation', handle_recommendation)

def unsubscribe():
    unsubscribe_from_event('recommendation', handle_recommendation)

def handle_recommendation(recommendation):
    logger = logging.getLogger(__name__)
    logger.info('Sending Slack Recommendation.')
    for channel in get_slack_channels(recommendation):
        payload = get_slack_payload(channel, recommendation['message'])
        send_recommendation_to_slack(channel, payload)
    return recommendation

def get_slack_payload(channel, message):
    payload = slack_util.get_payload_body(
        channel, message, icon=':female_student:'
    )
    return payload

#
# Get unique slack channels
# 
def get_slack_channels(recommendation):
    result = set([])
    attribute = 'slackChannels'
    try:
        if attribute not in recommendation:
            return []
        channels = recommendation[attribute].split(',')
        for channel in channels:
            channel = channel.strip()
            result.add(channel)
    except KeyError:
        return []

    return result

def send_recommendation_to_slack(channel, payload):
    logger = logging.getLogger(__name__)
    logger.info('Sending recommendation to channel "%s"', channel)
    web_hook = environment.get_env(environment.SLACK_WEB_HOOK)
    slack_util.call_slack_endpoint(channel, web_hook, payload)
