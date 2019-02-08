__author__ = 'tinglev@kth.se'

from modules import environment

def get_string_attribute(deployment, attribute):
    try:
        if not deployment[attribute]:
            return ''
        return deployment[attribute].replace('"', '').strip()
    except KeyError:
        return ''

def get_list_attribute(deployment, attribute):
    try:
        if not deployment[attribute]:
            return []
        return [item.replace('"', '').strip() for item in deployment[attribute].split(',')]
    except KeyError:
        return []

def get_test_accessibility(deployment):
    return get_string_attribute(deployment, 'testAccessibility')

def get_accessibility_urls(deployment):
    return get_list_attribute(deployment, 'accessibilityUrls')

def get_image_name(deployment):
    return get_string_attribute(deployment, 'imageName')

def get_graylog_image(deployment):
    return f'/.*{get_image_name(deployment)}:{get_application_version(deployment)}.*/'

def has_application_path(deployment):
    return get_string_attribute(deployment, 'applicationPath') != ''

def get_application_path(deployment):
    return get_string_attribute(deployment, 'applicationPath')

def get_monitor_path(deployment):
    monitor_path = get_string_attribute(deployment, 'monitorPath')
    if not monitor_path:
        return '/_monitor'
    return monitor_path

def get_slack_channels(deployment):
    return get_list_attribute(deployment, 'slackChannels')

def get_application_name(deployment):
    return get_string_attribute(deployment, 'applicationName')

def get_application_version(deployment):
    return get_string_attribute(deployment, 'version')

def get_cluster(deployment):
    return get_string_attribute(deployment, 'cluster')

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

def get_host_for_application(path, cluster):
    hosts = get_hosts()
    if not path or not cluster:
        return ''
    if path.startswith('/api/'):
        return hosts[cluster]['api']
    return hosts[cluster]['app']

def combine_host_and_paths(host, *paths):
    url = host.rstrip('/')
    for path in paths:
        url = f'{url}{path.rstrip("/")}'
    return url

def get_full_monitor_url(deployment):
    if not path_is_relative(get_monitor_path(deployment)):
        return get_monitor_path(deployment)
    host = get_host_for_application(get_application_path(deployment), get_cluster(deployment))
    return combine_host_and_paths(host, get_application_path(deployment),
                                  get_monitor_path(deployment))

def get_full_application_url(deployment):
    if not path_is_relative(get_application_path(deployment)):
        return get_application_path(deployment)
    host = get_host_for_application(get_application_path(deployment), get_cluster(deployment))
    return combine_host_and_paths(host, get_application_path(deployment))

def create_friendly_name(deployment):
    if get_public_name_english(deployment):
        return get_public_name_english(deployment)
    if get_public_name_swedish(deployment):
        return get_public_name_swedish(deployment)
    return get_application_name(deployment)
