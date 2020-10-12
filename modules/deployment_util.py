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
            return str(value).replace('"', '').strip()
        
        return ''

    except KeyError:
        return ''


def get_int_attribute(deployment, attribute):


    try:
        if not attribute:
            return None

        if attribute not in deployment:
            return None
        
        value =  deployment[attribute]

        return int(value)

    except KeyError:
        return None



def get_url_attribute(deployment, attribute):
    result = get_string_attribute(deployment, attribute)

    if result and result.startswith('http'):
        return result
        
    return ''

#
# Get unique items in set
# 
def get_list_attribute(deployment, attribute):
    result = set([])
    try:
        if attribute not in deployment:
            return sorted(set([]))

        items = deployment[attribute].split(',')

        for item in items:
            item = item.strip()
            result.add(item)
    except KeyError:
        return sorted(set([]))

    return sorted(result)



def get_test_accessibility(deployment):
    return get_string_attribute(deployment, 'testAccessibility')

def get_accessibility_urls(deployment):
    return get_list_attribute(deployment, 'accessibilityUrls')

def get_importance(deployment):
    return get_string_attribute(deployment, 'importance')

def get_team(deployment):
    return get_string_attribute(deployment, 'team')

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
    result = []
    for channel in get_list_attribute(deployment, 'slackChannels'):
        if channel.startswith("#"):
            result.append(channel)
    return result

def get_application_name(deployment):
    return get_string_attribute(deployment, 'applicationName')

def get_application_version(deployment):
    return get_string_attribute(deployment, 'version')

def get_replicas(deployment):
    return get_string_attribute(deployment, 'replicas')

def get_cluster(deployment):
    return get_string_attribute(deployment, 'cluster')

def get_friendly_name(deployment):
    return get_string_attribute(deployment, 'friendlyName')

def get_public_name_english(deployment):
    return get_string_attribute(deployment, 'publicNameEnglish')

def get_public_name_swedish(deployment):
    return get_string_attribute(deployment, 'publicNameSwedish')

def get_public_user_documentation_url(deployment):
    return get_string_attribute(deployment, 'publicUserDocumentationUrl')

def get_private_operations_documentation_url(deployment):
    return get_string_attribute(deployment, 'privateOperationsDocumentationUrl')

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
                                                          'https://integral.everest.sys.kth.se/'),
            'api': environment.get_env_with_default_value(environment.INTEGRAL_API_HOST,
                                                          'https://integral.everest.sys.kth.se/')
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

def wash_cluster(cluster):
    result = cluster
    if cluster not in get_hosts():
        result = 'active'
    
    return result
    
def get_host(deployment, path=''):
    if not path:
        path = get_application_path(deployment)
    return select_host(path, get_cluster(deployment))

def select_host(path, cluster):
    hosts = get_hosts()
    select_cluster = wash_cluster(cluster)
    
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

def get_about_url(deployment):
    return get_url_attribute(deployment, 'aboutUrl')

def get_monitor_url(deployment):
    return get_url_attribute(deployment, 'monitorUrl')


def get_application_url(deployment):
    return get_url_attribute(deployment, 'applicationUrl')