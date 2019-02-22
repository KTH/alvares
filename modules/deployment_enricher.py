__author__ = 'tinglev@kth.se'

import logging
from modules import deployment_util
from modules import deployment_util
from modules import environment

LOG = logging.getLogger(__name__)


def enrich(deployment):
    LOG.debug("Adding default values and common calculated values to the 'deployment' json.")
    
    # monitorPath - Not used any more
    # Can be removed later
    if 'monitorPath' in deployment:
        del deployment["monitorPath"]

    # applicationUrl
    if 'applicationUrl' not in deployment:
        deployment['applicationUrl'] = get_default_application_url(deployment)

    # monitorUrl
    if 'monitorUrl' not in deployment:
        deployment['monitorUrl'] = get_default_monitor_url(deployment)

    # friendlyName
    if 'friendlyName' not in deployment:
        deployment['friendlyName'] = get_default_friendly_name(deployment)
    
    # monitorPattern
    if 'monitorPattern' not in deployment:
        deployment['monitorPattern'] = get_default_monitor_pattern()

    # importance
    deployment = validate_importance_level(deployment)

    return deployment


def get_default_application_url(deployment):
    return deployment_util.combine_host_and_paths(
        deployment_util.get_host(deployment),
        deployment_util.get_application_path(deployment))

def get_default_monitor_url(deployment):

    monitor_route = '/_monitor'

    if deployment_util.get_application_path(deployment).endswith('/'):
        monitor_route = '_monitor'

    return deployment_util.combine_host_and_paths(
        deployment_util.get_host(deployment),
        deployment_util.get_application_path(deployment),
        monitor_route
    )

def get_default_friendly_name(deployment):
    if deployment_util.get_public_name_english(deployment):
        return deployment_util.get_public_name_english(deployment)

    if deployment_util.get_public_name_swedish(deployment):
        return deployment_util.get_public_name_swedish(deployment)
    
    return deployment_util.get_application_name(deployment)

def get_default_monitor_pattern():
    return environment.get_env_with_default_value(environment.UTR_KEYWORD, 'APPLICATION_STATUS: OK')

def validate_importance_level(deployment):
    if 'importance' not in deployment:
        deployment['importance'] = get_default_importance_level()
    else:
        deployment['importance'] = deployment['importance'].lower()

        if is_invalid_importance_level(deployment['importance']):
            deployment['importance'] = get_default_importance_level()

    return deployment

def get_default_importance_level():
    return 'low'

def is_invalid_importance_level(importance):
    if importance in ['low', 'medium', 'high']:
        return False
    return True