__author__ = 'tinglev@kth.se'

import logging
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from modules import deployment_util

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
    return ("https://kth-production.portal.mms.microsoft.com/"
            "?returnUrl=%2F#Workspace/search/index?"
            "_timeInterval.intervalDuration=604800&"
            "is=false&"
            "q=search%20dockerinfo_labels_se_kth_imageName_s%3D%3D%22{}%22%20"
            "and%20dockerinfo_labels_se_kth_imageVersion_s%3D%3D%22{}%22%20"
            "and%20dockerinfo_labels_se_kth_cluster_s%3D%3D%22{}%22%20"
            "%7C%20project%20time_t%2C%20msg_s%2C%20err_stack_s%20%7C%20render%20table%20"
            "%7C%20sort%20by%20time_t%20desc"
            .format(deployment.image_name, deployment.version, deployment.cluster))
