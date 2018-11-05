__author__ = 'tinglev@kth.se'

def get_slack_channels(error):
    if 'slackChannels' in error and error['slackChannels']:
        return [ch.rstrip() for ch in error['slackChannels'].split(',')]
    return []

def get_stack_trace(error):
    if 'stackTrace' in error and error['stackTrace']:
        return error['stackTrace']
    return ''

def get_message(error):
    if 'message' in error and error['message']:
        return error['message']
    return ''
