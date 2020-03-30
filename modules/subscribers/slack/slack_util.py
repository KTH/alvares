__author__ = 'tinglev@kth.se'

import logging
import urllib
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from modules import deployment_util, environment



def get_attachment(deployment,
                   fallback='Your client does not support attachments :(',
                   color='#aec90c'):
    application_name = deployment_util.get_application_name(deployment)
    application_version = deployment_util.get_application_version(deployment)
    return {
        "fallback": fallback,
        "color": color,
        "author_name": ":mag: Search Logs",
        "author_link": create_link_to_logs(deployment),
        "title": f"Image name: {application_name}",
        "text": f"Image version: {application_version}"
    }

def get_deployment_channels(deployment):
    channels = []
    channel_override = environment.get_env(environment.SLACK_CHANNEL_OVERRIDE)
    if channel_override:
        channels.append(channel_override)
        return channels
    for channel in environment.get_env_list(environment.SLACK_CHANNELS):
        if channel not in channels:
            channels.append(channel)
    for channel in deployment_util.get_slack_channels(deployment):
        if channel not in channels:
            channels.append(channel)
    return channels

def get_payload_body(channel, text, username='Cluster Deployment (Alvares)',
                     icon=':no_entry:'): #pragma: no cover
    return {
        "channel": channel,
        "text": text,
        "username": username,
        "icon_emoji": icon
    }

def add_attachment_to_body(body, attachment):
    if not 'attachments' in body:
        body['attachments'] = []
    body['attachments'].append(attachment)
    return body

def call_slack_endpoint(channel, web_hook, payload):
    logger = logging.getLogger(__name__)
    try:
        logger.debug('Calling Slack with payload "%s"', payload)
        response = requests.post(web_hook, json=payload)
        logger.debug('Response was "%s"', response.text)
    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        logger.error('Could not send slack notification to channel "%s": "%s"',
                     channel, request_ex)

def call_slack_channels(deployment, text, username):
    for channel in deployment_util.get_slack_channels(deployment):
        call_slack_endpoint(
            channel,
            environment.get_env(environment.SLACK_WEB_HOOK),
            get_payload_body(channel, text, username))

def create_link_to_logs(deployment):
    host = environment.get_env_with_default_value(environment.GRAYLOG_HOST,
                                                  'https://graycloud.ite.kth.se')
    graylog_image = deployment_util.get_graylog_image(deployment)
    url_safe_graylog_image = urllib.parse.quote(graylog_image)
    return (f'{host}/search?'
            f'rangetype=relative&fields=message%2Csource&'
            f'width=2560&highlightMessage=&relative=3600'
            f'&q=source%3A{deployment_util.get_cluster(deployment)}+'
            f'AND+image_name%3A{url_safe_graylog_image}')
