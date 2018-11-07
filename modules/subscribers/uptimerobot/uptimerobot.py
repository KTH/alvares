__author__ = 'tinglev'

import logging
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from modules import environment
from modules.subscribers.slack import slack_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import deployment_util

LOG = logging.getLogger(__name__)

# API Documentation: https://uptimerobot.com/api
API_BASE_URL = 'https://api.uptimerobot.com/v2'

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    global LOG # pylint: disable=W0603
    if not should_monitor(deployment):
        LOG.info('Skipping adding monitor for "%s"', deployment)
        return
    add_or_edit_monitor(deployment)
    call_slack_channel_with_monitor_url(deployment)
    return deployment

def create_slack_payload(message, channel):
    return {
        'username': 'Alvares',
        'text': message,
        'icon_emoji': ':azure:',
        'channel': channel
    }

def call_slack_channel_with_monitor_url(deployment):
    message = (f'*{create_friendly_name(deployment)}* in '
               f'*{deployment_util.get_cluster(deployment)}* is '
               f'UpTimeRobot monitored using {deployment_util.get_full_monitor_url(deployment)}')
    for channel in deployment_util.get_slack_channels(deployment):
        slack_util.call_slack_endpoint(channel,
                                       environment.get_env(environment.SLACK_WEB_HOOK),
                                       create_slack_payload(message, channel))

def should_monitor(deployment):
    published = has_application_path(deployment)
    cluster_ok = should_monitor_cluster(deployment)
    app_excluded = app_is_excluded(deployment)
    return published and cluster_ok and not app_excluded

def app_is_excluded(deployment):
    global LOG # pylint: disable=W0603
    app_excluded = (deployment_util.get_application_name(deployment) in
                    environment.get_env(environment.UTR_EXCLUDED_APPS))
    if app_excluded:
        LOG.debug('Application "%s" in UTR_EXCLUDED_APPS, '
                  'skipping UpTimeRobot integration',
                  deployment_util.get_application_name(deployment))
    return app_excluded

def has_application_path(deployment):
    global LOG # pylint: disable=W0603
    has_app_path = deployment_util.has_application_path(deployment)
    if not has_app_path:
        LOG.debug('Deployment has no published_url, skipping UpTimeRobot integration')
    return has_app_path

def should_monitor_cluster(deployment):
    global LOG # pylint: disable=W0603
    cluster_ok = (deployment_util.get_cluster(deployment) in
                  environment.get_env(environment.UTR_CLUSTERS))
    if not cluster_ok:
        LOG.debug('Cluster "%s" not in UTR_CLUSTERS, skipping UpTimeRobot integration',
                  deployment_util.get_cluster(deployment))
    return cluster_ok

def get_alert_contacts():
    response = call_endpoint('/getAlertContacts', {})
    # Type 11 = Slack integration
    return [c for c in response['alert_contacts']
            if c['type'] == 11 and c['friendly_name'].startswith('#')]

def search_for_existing_monitor(keyword):
    '''
    Check if a given monitor_url already has an entry on UTR
    '''
    global LOG # pylint: disable=W0603
    if keyword is None:
        return None
    payload = {'search': keyword}
    LOG.info('Searching for monitor with keyword "%s"', keyword)
    return call_endpoint('/getMonitors', payload)

def add_or_edit_monitor(deployment):
    try:
        global LOG # pylint: disable=W0603
        response = search_for_existing_monitor(deployment_util.get_full_monitor_url(deployment))
        if response['monitors']:
            modify_or_add_monitor(deployment, monitor_id=response['monitors'][0]['id'])
            return
        response = search_for_existing_monitor(deployment_util.create_friendly_name(deployment))
        if response['monitors']:
            modify_or_add_monitor(deployment, monitor_id=response['monitors'][0]['id'])
            return
        modify_or_add_monitor(deployment)
    except Exception:
        LOG.error('Could not add or edit monitor for: "%s"',
                  format(deployment.monitor_url), exc_info=True)

def modify_or_add_monitor(deployment, monitor_id=None):
    global LOG # pylint: disable=W0603
    keyword = environment.get_env_with_default_value(environment.UTR_KEYWORD,
                                                     'APPLICATION_STATUS: OK')
    payload = {
        'url': deployment_util.get_full_monitor_url(deployment),
        'friendly_name': deployment_util.create_friendly_name(deployment),
        'alert_contacts' : select_alert_contact(deployment),
        # Type 2 = Keyword
        'type': 2,
        # Type 2 = Keyword missing
        'keyword_type': 2,
        'keyword_value': keyword
    }
    if monitor_id:
        payload['id'] = monitor_id
        LOG.info('Editing monitor with id "%s"', monitor_id)
        call_endpoint('/editMonitor', payload)
    else:
        LOG.info('Adding monitor with friendly name "%s"',
                 deployment_util.create_friendly_name(deployment))
        call_endpoint('/newMonitor', payload)

def select_alert_contact(deployment):
    contacts = get_alert_contacts()
    slack_channels = deployment_util.get_slack_channels(deployment)
    for contact in contacts:
        for channel in slack_channels:
            if channel.replace('#', '') == contact['friendly_name'].replace('#', ''):
                return contact['id']
    return -1

def call_endpoint(api_url, payload):
    global LOG # pylint: disable=W0603
    if api_url.startswith('/'):
        base_url = environment.get_env_with_default_value(environment.UTR_API_BASE_URL,
                                                          'https://api.uptimerobot.com/v2')
        api_url = f'{base_url}{api_url}'
    LOG.debug('Calling endpoint "%s" with payload "%s"', api_url, payload)
    try:
        api_key = environment.get_env(environment.UTR_API_KEY)
        payload['api_key'] = api_key
        response = requests.post(api_url, data=payload)
        LOG.debug('Calling url "%s", got response was "%s"', api_url, response.text)
        return response.json()
    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not create UpTimeRobot monitor: "%s"', request_ex)
