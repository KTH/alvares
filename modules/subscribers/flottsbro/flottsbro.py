__author__ = 'tinglev'

import logging
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from modules import environment
from modules.subscribers.slack import slack_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import deployment_util

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    global LOG
    add(deployment)
    return deployment

def get_base_url():
    return environment.get_env_with_default_value(
        environment.FLOTTSBRO_API_BASE_URL,
        'https://api-r.referens.sys.kth.se/api/pipeline/')

def add(deployment):
    endpoint = '{}/v1/latest/{}/{}/'.format(
        get_base_url(),
        deployment.cluster,
        deployment.applicationName)

    call_endpoint(endpoint, deployment)

def call_endpoint(endpoint, deployment):
    global LOG

    try:
        headers = {
            'api_key':  environment.get_env(environment.FLOTTSBRO_API_KEY)
        }
        response = requests.post(endpoint, data=deployment, headers=headers)

        LOG.info('Calling url "%s", got response was "%s"', endpoint, response.text)

    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not add deployment to Flottsbro-API: "%s"', request_ex)
