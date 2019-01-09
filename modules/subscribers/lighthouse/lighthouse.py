__author__ = 'tinglev'

import logging
import requests
import tempfile
from requests import HTTPError, ConnectTimeout, RequestException
from modules import environment
from modules.subscribers.slack import slack_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import deployment_util, process

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    global LOG
    if not deployment_util.get_test_accessibility(deployment):
        LOG.debug('testAccessibility not set - skipping Lighthouse')
        return deployment
    if not environment.get_env(environment.SLACK_TOKEN):
        LOG.info('No SLACK_TOKEN env provided. Cant run lighthouse')
        return deployment
    app_url = deployment_util.get_full_application_url(deployment)
    if app_url:
        with tempfile.mkdtemp() as tmp_dir:
            LOG.debug('Temp dir created, running headless-lighthouse')
            process.run_with_output(f'docker run -e URL={app_url} '
                                    f'-v {tmp_dir}:/report '
                                    f'kthregistryv2.sys.kth.se/headless-lighthouse:1.0.8_578859d')
            report_path = f'{tmp_dir}/report.html'
            for channel in slack_util.get_deployment_channels(deployment):
                send_file_to_slack(channel, deployment, report_path)
    return deployment

def send_file_to_slack(channel, deployment, report_path):
    global LOG
    LOG.debug('Starting upload of lighthouse report to Slack')
    api_base_url = environment.get_env(environment.SLACK_API_BASE_URL)
    url = f'{api_base_url}/files.upload'
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    payload = get_payload(channel, deployment, report_path)
    LOG.debug('File upload payload is: "%s"', payload)
    try:
        LOG.debug('Calling Slack with payload "%s"', payload)
        response = requests.post(url, data=payload, headers=headers)
        LOG.debug('Response was "%s"', response.text)
    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not send slack notification to channel "%s": "%s"',
                  channel, request_ex)

def get_payload(channel, deployment, report_path):
    slack_token = environment.get_env(environment.SLACK_TOKEN)
    image_name = deployment_util.get_image_name(deployment)
    with open(report_path, 'r') as report_file:
        file_content = report_file.read().encode()
    return {
        'token': slack_token,
        'channels': channel,
        'content': file_content,
        'filename': 'lighthouse_report.html',
        'filetype': 'html',
        'title': f'Lighthouse report for application {image_name}'
    }
