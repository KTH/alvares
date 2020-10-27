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
    for channel in slack_util.get_deployment_channels(deployment):
        send_deployment_to_slack(web_hook, channel, deployment)
    return deployment

def send_payload(channel, payload):
    web_hook = environment.get_env(environment.SLACK_WEB_HOOK)
    slack_util.call_slack_endpoint(channel, web_hook, payload)


def send_deployment_to_slack(web_hook, channel, deployment):
    global LOG # pylint: disable=W0603
    LOG.debug('Sending Slack deployment notification to channel "%s"', channel)
    message = create_deployment_message(deployment)
    payload = create_deployment_payload(channel, message, deployment, username="Deployment started")
    slack_util.call_slack_endpoint(channel, web_hook, payload)

def create_deployment_payload(channel, message, deployment, username='Deployment'): #pragma: no cover
    body = slack_util.get_payload_body(channel, message, icon=':azure:', username=username)
    attachment = slack_util.get_attachment(deployment)
    body = slack_util.add_attachment_to_body(body, attachment)
    return body

def create_deployment_message(deployment): # pragma: no cover
    if deployment_util.has_zero_replicas(deployment):
        return (f':closed_book: Started removing *{deployment_util.get_friendly_name(deployment)}* from *{deployment_util.get_cluster(deployment)}*, this may take up to 30 seconds.\n<https://confluence.sys.kth.se/confluence/pages/viewpage.action?pageId=44894619|Information how to remove a service')

    return (f'{deployment_util.get_replicas(deployment)} replica(s) of *{deployment_util.get_friendly_name(deployment)}* are being deployed'
            f' in *{deployment_util.get_cluster(deployment)}*, this may take up to 30 seconds.')
