__author__ = 'tinglev@kth.se'

import logging
from modules import environment
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules.subscribers.slack.slack_util import call_slack_endpoint, get_payload_body
from modules import error_util

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('error', handle_error)

def unsubscribe():
    unsubscribe_from_event('error', handle_error)

def handle_error(error):
    global LOG # pylint: disable=W0603
    web_hook = environment.get_env(environment.SLACK_WEB_HOOK)
    overridden = send_to_override(web_hook, error)
    if not overridden:
        error_has_channels = send_to_error_channels(web_hook, error)
        if not error_has_channels:
            send_to_environment_channels(web_hook, error)


def send_to_environment_channels(web_hook, error):
    for slack_channel in environment.get_env_list(environment.SLACK_CHANNELS):
        send_error_to_slack(web_hook, slack_channel, error)

def send_to_error_channels(web_hook, error):
    slack_channels = error_util.get_slack_channels(error)
    if slack_channels:
        for slack_channel in slack_channels:
            send_error_to_slack(web_hook, slack_channel, error)
        return True
    return False

def send_to_override(web_hook, error):
    channel_override = environment.get_env(environment.SLACK_CHANNEL_OVERRIDE)
    if channel_override:
        send_error_to_slack(web_hook, channel_override, error)
        return error
    return None

def send_error_to_slack(web_hook, channel, error):
    global LOG # pylint: disable=W0603
    LOG.debug('Sending Slack notification for error to channel "%s"', channel)
    message = create_error_message(error)
    payload = create_error_payload(channel, message)
    call_slack_endpoint(channel, web_hook, payload)

def create_error_payload(channel, message): #pragma: no cover
    body = get_payload_body(channel, message, icon=':no_entry:', username='Alvares Error')
    return body

def create_error_message(error):
    stack_trace = error_util.get_stack_trace(error)
    message = error_util.get_message(error)
    if not stack_trace:
        return f'{message}'
    return f'*{message}* \n```\n{stack_trace}\n```'
