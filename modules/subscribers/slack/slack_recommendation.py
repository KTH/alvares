__author__ = 'tinglev@kth.se'

import logging
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import environment
from modules.subscribers.slack import slack_util

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('recommendation', handle_recommendation)

def unsubscribe():
    unsubscribe_from_event('recommendation', handle_recommendation)

def handle_recommendation(recommendation):
    global LOG # pylint: disable=W0603
    for channel in get_slack_channels(recommendation):
        send_recommendation_to_slack(channel, recommendation['message'])
    return recommendation


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

def send_recommendation_to_slack(channel, message):
    global LOG # pylint: disable=W0603
    LOG.debug('Sending Slack notification to channel "%s"', channel)
    web_hook = environment.get_env(environment.SLACK_WEB_HOOK)
    slack_util.call_slack_endpoint(channel, web_hook, message)