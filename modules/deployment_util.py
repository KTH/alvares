__author__ = 'tinglev@kth.se'

from modules import environment

def get_string_attribute(deployment, attribute):
    try:
        if not deployment[attribute]:
            return ''
        return deployment[attribute]
    except KeyError:
        return ''

def get_list_attribute(deployment, attribute):
    try:
        if not deployment[attribute]:
            return []
        return [item.rstrip() for item in deployment[attribute].split(',')]
    except KeyError:
        return []

def has_published_url(deployment):
    return get_string_attribute(deployment, 'publishedUrl') != ''

def get_published_url(deployment):
    return get_string_attribute(deployment, 'publishedUrl')

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

def get_full_monitor_url(deployment):
    hosts = get_hosts()
    host = 'active'
    mode = 'app'
    if 'monitorUrl' in deployment and deployment['monitorUrl']:
        if deployment['monitorUrl'].startswith('/'):
            if deployment['monitorUrl'].startswith('/api/'):
                mode = 'api'
            if get_cluster(deployment) == 'stage':
                host = 'stage'
            return f'{hosts[host][mode]}{deployment["monitorUrl"]}'
        return deployment['monitorUrl']
    return ''
