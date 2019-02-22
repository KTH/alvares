__author__ = 'tinglev@kth.se'

import logging
from modules import environment

LOG = logging.getLogger(__name__)

def get_string_attribute(deployment, attribute):


    try:
        if not attribute:
            return ''

        if attribute not in deployment:
            return ''
        
        value =  deployment[attribute]

        if value:
            return value.replace('"', '').strip()
        
        return ''

    except KeyError:
        return ''

def get_url_attribute(deployment, attribute):
    result = get_string_attribute(deployment, attribute)

    if result and result.startswith('http'):
        return result
        
    return ''

def get_list_attribute(deployment, attribute):
    try:
        if attribute not in deployment:
            return []
        return [item.replace('"', '').strip() for item in deployment[attribute].split(',')]
    except KeyError:
        return []

def get_test_accessibility(deployment):
    return get_string_attribute(deployment, 'testAccessibility')

def get_accessibility_urls(deployment):
    return get_list_attribute(deployment, 'accessibilityUrls')

def get_importance(deployment):
    return get_string_attribute(deployment, 'importance')
 
def get_image_name(deployment):
    return get_string_attribute(deployment, 'imageName')

def get_graylog_image(deployment):
    return f'/.*{get_image_name(deployment)}:{get_application_version(deployment)}.*/'

def has_application_path(deployment):
    return get_string_attribute(deployment, 'applicationPath') != ''

def get_application_path(deployment):
    return get_string_attribute(deployment, 'applicationPath')

def get_monitor_pattern(deployment):
    return get_string_attribute(deployment, 'monitorPattern')

def get_slack_channels(deployment):
    return get_list_attribute(deployment, 'slackChannels')

def get_application_name(deployment):
    return get_string_attribute(deployment, 'applicationName')

def get_application_version(deployment):
    return get_string_attribute(deployment, 'version')

def get_cluster(deployment):
    return get_string_attribute(deployment, 'cluster')

def get_friendly_name(deployment):
    return get_string_attribute(deployment, 'friendlyName')
    
def get_public_name_english(deployment):
    return get_string_attribute(deployment, 'publicNameEnglish')

def get_public_name_swedish(deployment):
    return get_string_attribute(deployment, 'publicNameSwedish')

def get_detectify_tokens(deployment):
    return get_list_attribute(deployment, 'detectifyProfileTokens')

def get_hosts():
    return {
        'active': {
            'app': environment.get_env_with_default_value(environment.ACTIVE_APP_HOST,
                                                          'https://app.kth.se'),
            'api': environment.get_env_with_default_value(environment.ACTIVE_API_HOST,
                                                          'https://api.kth.se')
        },
        'stage': {
            'app': environment.get_env_with_default_value(environment.STAGE_APP_HOST,
                                                          'https://app-r.referens.sys.kth.se'),
            'api': environment.get_env_with_default_value(environment.STAGE_API_HOST,
                                                          'https://api-r.referens.sys.kth.se')
        },
        'integral': {
            'app': environment.get_env_with_default_value(environment.INTEGRAL_APP_HOST,
                                                          'https://integral.sys.kth.se'),
            'api': environment.get_env_with_default_value(environment.INTEGRAL_API_HOST,
                                                          'https://integral.sys.kth.se')
        },
        'integral-stage': {
            'app': environment.get_env_with_default_value(environment.INTEGRAL_STAGE_APP_HOST,
                                                          'https://integral-r.referens.sys.kth.se'),
            'api': environment.get_env_with_default_value(environment.INTEGRAL_STAGE_API_HOST,
                                                          'https://integral-r.referens.sys.kth.se')
        }


    }

def get_full_url_for_path(path, cluster):
    hosts = get_hosts()
    if not path or not cluster:
        return ''
    if not path.startswith('/'):
        # Absolut url
        return path
    if path.startswith('/api/'):
        return hosts[cluster]['api']
    return hosts[cluster]['app']

def path_is_relative(path):
    return path.startswith('/')

def path_is_url(path):
    return path.startswith('http')

def get_host(deployment):
     return get_host_for_application(get_application_path(deployment), get_cluster(deployment))

def get_host_for_application(path, cluster):
    hosts = get_hosts()
    select_cluster = cluster
    if cluster not in hosts:
        select_cluster = 'active'
    
    if not path or not cluster:
        return ''
    if path.startswith('/api/'):
        return hosts[select_cluster]['api']
    return hosts[select_cluster]['app']

def combine_host_and_paths(host, *paths):
    url = host.rstrip('/')
    for path in paths:
        url = f'{url}{path.rstrip()}'
    return url

def get_monitor_url(deployment):
    return get_url_attribute(deployment, 'monitorUrl')


def get_application_url(deployment):
    return get_url_attribute(deployment, 'applicationUrl')