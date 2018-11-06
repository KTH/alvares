__author__ = 'tinglev@kth.se'

from modules import environment

def get_slack_channels(deployment):
    if 'slackChannels' in deployment and deployment['slackChannels']:
        return [ch.rstrip() for ch in deployment['slackChannels'].split(',')]
    return []

def get_application_name(deployment):
    if 'applicationName' in deployment and deployment['applicationName']:
        return deployment['applicationName']
    return ''

def get_application_version(deployment):
    if 'version' in deployment and deployment['version']:
        return deployment['version']
    return ''

def get_cluster(deployment):
    if 'cluster' in deployment and deployment['cluster']:
        return deployment['cluster']
    return ''

def get_public_name_english(deployment):
    if 'publicNameEnglish' in deployment and deployment['publicNameEnglish']:
        return deployment['publicNameEnglish']
    return ''

def get_public_name_swedish(deployment):
    if 'publicNameSwedish' in deployment and deployment['publicNameSwedish']:
        return deployment['publicNameSwedish']
    return ''

def get_detectify_tokens(deployment):
    if 'detectifyProfileTokens' in deployment and deployment['detectifyProfileTokens']:
        return [t.rstrip() for t in deployment['detectifyProfileTokens'].split(',')]
    return []

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
