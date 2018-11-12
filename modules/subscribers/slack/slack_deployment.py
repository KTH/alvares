__author__ = 'tinglev@kth.se'

import logging
from modules import environment
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules.subscribers.slack import slack_util
from modules import deployment_util

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    global LOG # pylint: disable=W0603
    web_hook = environment.get_env(environment.SLACK_WEB_HOOK)
    overridden = send_to_channel_override(web_hook, deployment)
    if not overridden:
        sent_to = send_to_global_channels(web_hook, deployment)
        send_to_deployment_channels(web_hook, deployment, sent_to)
    return deployment

def send_to_global_channels(web_hook, deployment):
    sent_to = []
    for channel in environment.get_env_list(environment.SLACK_CHANNELS):
        send_deployment_to_slack(web_hook, channel, deployment)
        sent_to.append(channel)
    return sent_to

def send_to_channel_override(web_hook, deployment):
    channel_override = environment.get_env(environment.SLACK_CHANNEL_OVERRIDE)
    if channel_override:
        send_deployment_to_slack(web_hook, channel_override, deployment)
        return deployment
    return None

def send_to_deployment_channels(web_hook, deployment, already_sent_to):
    for channel in deployment_util.get_slack_channels(deployment):
        if not channel in already_sent_to:
            send_deployment_to_slack(web_hook, channel, deployment)

def send_deployment_to_slack(web_hook, channel, deployment):
    global LOG # pylint: disable=W0603
    LOG.debug('Sending Slack notification to channel "%s"', channel)
    message = create_deployment_message(deployment)
    payload = create_deployment_payload(channel, message, deployment)
    slack_util.call_slack_endpoint(channel, web_hook, payload)

def create_deployment_payload(channel, message, deployment): #pragma: no cover
    body = slack_util.get_payload_body(channel, message, icon=':azure:',
                                       username='Cluster Deployment')
    attachment = slack_util.get_attachment(deployment)
    body = slack_util.add_attachment_to_body(body, attachment)
    return body

def create_deployment_message(deployment): # pragma: no cover
    return (f'*{deployment_util.get_application_name(deployment)}* deployed'
            f' in *{deployment_util.get_cluster(deployment)}*')
