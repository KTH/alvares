__author__ = 'tinglev@kth.se'

import logging
from modules import deployment_util
from modules import environment

LOG = logging.getLogger(__name__)

def enrich(deployment):
    LOG.debug(
        "Adding default values and common calculated values to the 'deployment' json.")

    # monitorPath - Not used any more
    # Can be removed later
    if 'monitorPath' in deployment:
        del deployment["monitorPath"]

    # applicationUrl
    if 'applicationUrl' not in deployment:
        add_application_url(deployment)

    # monitorUrl
    if 'monitorUrl' not in deployment:
        add_monitor_url(deployment)

    # monitorUrl
    if 'aboutUrl' not in deployment:
        add_about_url(deployment)

    # friendlyName
    if 'friendlyName' not in deployment:
        add_friendly_name(deployment)

    # monitorPattern
    if 'monitorPattern' not in deployment:
        add_monitor_pattern(deployment)

    # monitorPattern
    if 'team' not in deployment and 'slackChannels' in deployment:
        add_team_from_slack_channels(deployment)

    # importance
    clean_or_add_importance_level_(deployment)

    return deployment


def add_application_url(deployment):
    application_url = deployment_util.combine_host_and_paths(deployment_util.get_host(deployment), deployment_util.get_application_path(deployment))
    deployment['applicationUrl'] = application_url

def add_monitor_url(deployment):

    monitor_url = ''

    monitor_route = '/_monitor'

    if deployment_util.get_application_path(deployment).endswith('/'):
        monitor_route = '_monitor'

    monitor_url = deployment_util.combine_host_and_paths(
        deployment_util.get_host(deployment),
        deployment_util.get_application_path(deployment),
        monitor_route
    )

    deployment['monitorUrl'] = monitor_url

def add_about_url(deployment):

    about_url = ''
    monitor_url = deployment_util.get_monitor_url(deployment)

    if not monitor_url.endswith('/_monitor'):
        return about_url

    about_route = '/_about'

    if deployment_util.get_application_path(deployment).endswith('/'):
        about_route = '_about'

    about_url = deployment_util.combine_host_and_paths(
        deployment_util.get_host(deployment),
        deployment_util.get_application_path(deployment),
        about_route
    )

    print(about_url)
    deployment['aboutUrl'] = about_url

def add_friendly_name(deployment):

    friendly_name = ''
 
    if deployment_util.get_public_name_english(deployment):
        friendly_name = deployment_util.get_public_name_english(deployment)
    elif deployment_util.get_public_name_swedish(deployment):
        friendly_name = deployment_util.get_public_name_swedish(deployment)
    else:
        friendly_name = deployment_util.get_application_name(deployment)

    deployment['friendlyName'] = friendly_name


def add_monitor_pattern(deployment):
    monitor_pattern = environment.get_env_with_default_value(environment.UTR_KEYWORD, 'APPLICATION_STATUS: OK')
    deployment['monitorPattern'] = monitor_pattern


def clean_or_add_importance_level_(deployment):
    if 'importance' not in deployment:
        deployment['importance'] = get_default_importance_level()
    else:
        deployment['importance'] = deployment['importance'].lower()

        if is_invalid_importance_level(deployment['importance']):
            deployment['importance'] = get_default_importance_level()


def get_default_importance_level():
    return 'low'


def is_invalid_importance_level(importance):
    if importance in ['low', 'medium', 'high']:
        return False
    return True


def add_team_from_slack_channels(deployment):

    team = ''

    # Use first match.
    for channel in deployment_util.get_slack_channels(deployment):

        if "team-pipeline" in channel:
            team = "team-pipeline"
            break

        if "team-studadm" in channel:
            team = "team-studadm"
            break

        if "team-e-larande" in channel:
            team = "team-e-larande"
            break

        if "team-integration" in channel:
            team = "team-integration"
            break

        if "team-kth-webb" in channel:
            team = "team-kth-webb"
            break

    deployment['team'] = team