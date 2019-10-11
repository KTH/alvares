__author__ = 'tinglev'

import logging
from modules import environment, deployment_util
from modules.subscribers.slack import slack_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    call_slack_channel_with_application_endpoint_url(deployment)

def has_application_path(deployment):
    if 'applicationPath' in deployment:
        if deployment['applicationPath']:
            return True
    return False

def build_information_link(deployment):
    host = deployment_util.get_host(deployment)
    if not host:
        host = deployment_util.get_host(deployment, path='/')

    path = f'/pipeline/#{deployment_util.get_application_name(deployment)}'

    return deployment_util.combine_host_and_paths(host, path)


def call_slack_channel_with_application_endpoint_url(deployment):
    
    host = deployment_util.get_host(deployment)
    if not host:
        host = deployment_util.get_host(deployment, path='/')

    path = f'/pipeline/#{deployment_util.get_application_name(deployment)}'

    message = (f':information_source: About *{deployment_util.get_friendly_name(deployment)}* '
               f'{build_information_link(deployment)} '
               f'in *{deployment_util.get_cluster(deployment)}*')

    for channel in deployment_util.get_slack_channels(deployment):
        slack_util.call_slack_endpoint(channel,
                                       environment.get_env(environment.SLACK_WEB_HOOK),
                                       create_slack_payload(message, channel))
    
def create_slack_payload(message, channel):
    return {
        'username': 'Cluster Deployment (Alvares)',
        'text': message,
        'icon_emoji': ':azure:',
        'channel': channel
    }
