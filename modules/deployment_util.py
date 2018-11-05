__author__ = 'tinglev@kth.se'

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

def get_detectify_tokens(deployment):
    if 'detectifyProfileTokens' in deployment and deployment['detectifyProfileTokens']:
        return [t.rstrip() for t in deployment['detectifyProfileTokens'].split(',')]
    return []
