__author__ = 'tinglev@kth.se'

import logging
import urllib
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from modules import deployment_util, environment

LOG = logging.getLogger(__name__)

def get_attachment(deployment,
                   fallback='Your client does not support attachments :(',
                   color='#36a64f'):
    application_name = deployment_util.get_application_name(deployment)
    application_version = deployment_util.get_application_version(deployment)
    return {
        "fallback": fallback,
        "color": color,
        "author_name": "View logs for this deployment",
        "author_link": create_link_to_logs(deployment),
        "title": f"Application name: {application_name}",
        "text": f"Application version: {application_version}"
    }

def get_payload_body(channel, text, username='Dizin',
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
    global LOG # pylint: disable=W0603
    try:
        LOG.debug('Calling Slack with payload "%s"', payload)
        response = requests.post(web_hook, json=payload)
        LOG.debug('Response was "%s"', response.text)
    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not send slack notification to channel "%s": "%s"',
                  channel, request_ex)

def create_link_to_logs(deployment):
    host = environment.get_env_with_default_value(environment.GRAYLOG_HOST,
                                                  'https://graycloud.ite.kth.se')
    graylog_image = deployment_util.get_graylog_image(deployment)
    print(graylog_image)
    url_safe_graylog_image = urllib.parse.quote(graylog_image)
    return (f'{host}/search?'
            f'rangetype=relative&fields=message%2Csource&'
            f'width=2560&highlightMessage=&relative=300'
            f'&q=source%3A{deployment_util.get_cluster(deployment)}+'
            f'AND+image_name%3A{url_safe_graylog_image}')
