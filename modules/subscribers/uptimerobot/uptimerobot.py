__author__ = 'tinglev'

import os
import logging
import requests
from modules import environment
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event

LOG = logging.getLogger(__name__)

# API Documentation: https://uptimerobot.com/api
API_BASE_URL = 'https://api.uptimerobot.com/v2'

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    global LOG
    if not should_monitor(deployment):
        LOG.info('Skipping adding monitor for "%s"', deployment)
        return
    #add_or_edit_monitor(deployment)
    #call_slack_channel_with_monitor_url(deployment)
    return deployment

def should_monitor(deployment):
    published = has_publish_url(deployment)
    cluster_ok = should_monitor_cluster(deployment)
    app_excluded = app_is_excluded(deployment)
    return published and cluster_ok and not app_excluded

def app_is_excluded(deployment):
    global LOG
    app_excluded = (deployment.application_name in
                    environment.get_env(environment.UTR_EXCLUDED_APPS))
    if app_excluded:
        LOG.debug('Application "%s" in UTR_EXCLUDED_APPS, '
                  'skipping UpTimeRobot integration',
                  deployment.application_name)
    return app_excluded

def has_publish_url(deployment):
    global LOG
    app_has_publish_url = hasattr(deployment, 'published_url') and deployment.published_url
    if not app_has_publish_url:
        LOG.debug('Deployment has no published_url, skipping UpTimeRobot integration')
    return app_has_publish_url

def should_monitor_cluster(deployment):
    global LOG
    cluster_ok = deployment.cluster in environment.get_env(environment.UTR_CLUSTERS)
    if not cluster_ok:
        LOG.debug('Cluster "%s" not in UTR_CLUSTERS, skipping UpTimeRobot integration',
                  deployment.cluster)
    return cluster_ok

"""
class UpTimeRobot(AbstractMiddleware):

    API_BASE_URL = 'https://api.uptimerobot.com/v2'

    MONITOR_TYPE_KEYWORD = 2 # Keyword
    MONITOR_KEYWORD_PATTERN = 'APPLICATION_STATUS: OK'
    MONITOR_ALERT_ON_KEYWORD_EXISTS = 1
    MONITOR_ALERT_ON_KEYWORD_MISSING = 2

    ALERT_TEAM_KTH_WEBB_ID = 2518353
    ALERT_TEAM_STUDADM = 2518354
    ALERT_TEAM_E_LARANDE = 2518355
    ALERT_TEAM_PIPELINE = 2518352
    ALERT_SECTION_SFU = 2592556

    def __init__(self, name):
        self.log = logging.getLogger(__name__)
        environment_variables = [os_environment.ENV_UPTIMEROBOT_API_KEY,
                                 os_environment.ENV_UTR_CLUSTERS,
                                 os_environment.ENV_UTR_EXCLUDED_APPS,
                                 os_environment.ENV_UTR_KTH_APP_HOST]
        self.kth_app_server = os_environment.get_utr_kth_app_host()
        super(UpTimeRobot, self).__init__(name, environment_variables)

    #
    # SUPER CLASS OVERRIDES
    #

    def process_deployment(self, deployment):
        self.log_deployment_start(deployment)
        if not self.should_monitor(deployment):
            self.log.info('Skipping adding monitor for "%s"', deployment)
            return

        self.add_or_edit_monitor(deployment)
        self.call_slack_channel_with_monitor_url(deployment)
        return deployment

    def process_error(self, error):
        self.log_error_start(error)

    #
    # PRIVATE METHODS
    #

    def create_slack_payload(self, message, channel):
        return {
                'username': 'Dizin',
                'text': message,
                'icon_emoji': ':azure:',
                'channel': channel
            }

    def call_slack_channel_with_monitor_url(self, deployment):
        message = ("*{}* in *{}* is UpTimeRobot monitored using {}.".format(
                    self.create_friendly_name(deployment),
                    deployment.cluster,
                    deployment.monitor_url))

        for channel in deployment.get_slack_channels():
            slack = Slack('Slack for UpTimeRobot')
            slack.call_slack_endpoint(channel,
                                    os_environment.get_slack_web_hook(),
                                    self.create_slack_payload(message, channel))


    def add_or_edit_monitor(self, deployment):
        try:

            response = self.get_monitor_by_url(deployment.monitor_url)

            if response["monitors"]:
                self.edit_monitor(deployment, response["monitors"][0]["id"])
                return

            if not response["monitors"]:
                response = self.get_monitor_by_friendly_name(self.create_friendly_name(deployment))

            if response["monitors"]:
                self.edit_monitor(deployment, response["monitors"][0]["id"])
                return

            self.add_monitor(deployment)

        except:
            self.log.error('Could not add or edit monitor for: "%s"', format(deployment.monitor_url), exc_info=True)

    def add_monitor(self, deployment):

        url = '{}{}'.format(self.API_BASE_URL, '/newMonitor')

        payload = {
            'api_key': os_environment.get_utr_api_key(),
            'url': deployment.monitor_url,
            'friendly_name': self.create_friendly_name(deployment),
            'alert_contacts' : self.select_alert_contact(deployment),
            'type': UpTimeRobot.MONITOR_TYPE_KEYWORD,
            'keyword_type': UpTimeRobot.MONITOR_ALERT_ON_KEYWORD_MISSING,
            'keyword_value': UpTimeRobot.MONITOR_KEYWORD_PATTERN
        }
        
        self.log.info('Add monitor "%s" ("%s")', payload["friendly_name"], payload["url"])
        self.call_endpoint(url , payload)

    def edit_monitor(self, deployment, monitor_id):
        
        url = '{}{}'.format(self.API_BASE_URL, '/editMonitor')

        payload = {
            'api_key': os_environment.get_utr_api_key(),
            'id': monitor_id,
            'url': deployment.monitor_url,
            'friendly_name': self.create_friendly_name(deployment),
            'alert_contacts' : self.select_alert_contact(deployment),
            'type': UpTimeRobot.MONITOR_TYPE_KEYWORD,
            'keyword_type': UpTimeRobot.MONITOR_ALERT_ON_KEYWORD_MISSING,
            'keyword_value': UpTimeRobot.MONITOR_KEYWORD_PATTERN
        }

        self.log.info('Edit monitor with id "%s"', monitor_id)
        self.call_endpoint(url, payload)

    def get_monitor_by_url(self, monitor_url):
        '''
        Search and find a monitor based on url.
        ex:
        curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -d 'api_key=u431486-b7ea23fc4ff454d244b88061&format=json&logs=0&search=https://app.kth.se/kth-azure-app/_monitore' "https://api.uptimerobot.com/v2/getMonitors" | jq
        '''

        if monitor_url is None:
            return None

        url = '{}{}'.format(self.API_BASE_URL, '/getMonitors')

        payload = {
            'api_key': os_environment.get_utr_api_key(),
            'search': monitor_url,
            'format': "json"
        }

        self.log.info('Get monitor with url "%s"', monitor_url)
        return self.call_endpoint(url, payload)

    def get_monitor_by_friendly_name(self, friendly_name):
        '''
        Search and find a monitor based on url.
        ex:
        curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -d 'api_key=u431486-b7ea23fc4ff454d244b88061&format=json&logs=0&search=https://app.kth.se/kth-azure-app/_monitore' "https://api.uptimerobot.com/v2/getMonitors" | jq
        '''

        if friendly_name is None:
            return None

        url = '{}{}'.format(self.API_BASE_URL, '/getMonitors')

        payload = {
            'api_key': os_environment.get_utr_api_key(),
            'search': friendly_name,
            'format': "json"
        }

        self.log.info('Get monitor with friendly_name "%s"', friendly_name)
        return self.call_endpoint(url, payload)


    def call_endpoint(self, api_url, payload):
        self.log.debug('Calling endpoint "%s" with payload "%s"', api_url, payload)
        try:
            if not self.is_dry_run():
                response = requests.post(api_url, data=payload)
                self.log.debug('Calling url "%s", got response was "%s"', api_url, response.text)
                return response.json()
                
        except (HTTPError, ConnectTimeout, RequestException) as request_ex:
            self.log.error('Could not create UpTimeRobot monitor: "%s"', request_ex)
            
    def should_monitor(self, deployment): #pragma: no cover
        published = self.has_publish_url(deployment)
        cluster_ok = self.should_monitor_cluster(deployment)
        app_excluded = self.app_is_excluded(deployment)
        return published and cluster_ok and not app_excluded

    def app_is_excluded(self, deployment):
        app_excluded = deployment.application_name in os_environment.get_utr_excluded_apps()
        if app_excluded:
            self.log.debug('Application "%s" in UTR_EXCLUDED_APPS, '
                           'skipping UpTimeRobot integration',
                           deployment.application_name)
        return app_excluded

    def has_publish_url(self, deployment):
        has_publish_url = hasattr(deployment, 'published_url') and deployment.published_url
        if not has_publish_url:
            self.log.debug('Deployment has no published_url, skipping UpTimeRobot integration')
        return has_publish_url

    def should_monitor_cluster(self, deployment):
        cluster_ok = deployment.cluster in os_environment.get_utr_clusters()
        if not cluster_ok:
            self.log.debug('Cluster "%s" not in UTR_CLUSTERS, skipping UpTimeRobot integration'
                           , deployment.cluster)
        return cluster_ok

    def select_alert_contact(self, deployment):

        slack_channels = ''.join(deployment.get_slack_channels())
        
        if "team-kth-webb" in slack_channels:
            return UpTimeRobot.ALERT_TEAM_KTH_WEBB_ID
        
        if "team-studadm" in slack_channels:
            return UpTimeRobot.ALERT_TEAM_STUDADM
        
        if "team-e-larande" in slack_channels:
            return UpTimeRobot.ALERT_TEAM_E_LARANDE

        if "team-pipeline" in slack_channels:
            return UpTimeRobot.ALERT_TEAM_PIPELINE

        return UpTimeRobot.ALERT_SECTION_SFU

        
    def create_friendly_name(self, deployment):
        if deployment.public_name_english:
            return deployment.public_name_english
        
        if deployment.public_name_swedish:
            return deployment.public_name_swedish
        
        return '{}'.format(deployment.application)

"""
