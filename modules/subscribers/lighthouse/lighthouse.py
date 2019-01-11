__author__ = 'tinglev'

import os
import re
import json
import shutil
import logging
import tempfile
import datetime
import requests
from boxsdk import JWTAuth
from boxsdk import Client as BoxClient
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
        try:
            tmp_dir = tempfile.mkdtemp()
            LOG.debug('Temp dir created, running headless-lighthouse')
            output = process.run_with_output(f'docker run -e URL={app_url} '
                                             f'-v {tmp_dir}:/report '
                                             f'docker.io/kthse/headless-lighthouse:1.0.10_61260d1')
            LOG.debug('Output from lighthouse was: "%s"', output)
            report_path = f'{tmp_dir}/report.html'
            box_link = upload_to_box(report_path)
            for channel in slack_util.get_deployment_channels(deployment):
                send_file_to_slack(channel, deployment, report_path, box_link)
        finally:
            if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir)
    return deployment

def upload_to_box(report_path):
    box_auth_string = environment.get_env(environment.BOX_AUTH_JSON)
    box_auth_json = json.loads(box_auth_string.replace("'", ""))
    box_sdk = JWTAuth.from_settings_dictionary(box_auth_json)
    client = BoxClient(box_sdk)
    file_name = create_file_name(create_file_name)
    box_file = client.folder('63669613923').upload(report_path, file_name)
    return box_file.get_sharable_link(access='open')

def send_file_to_slack(channel, deployment, report_path, box_link):
    global LOG
    LOG.debug('Starting upload of lighthouse report to Slack')
    api_base_url = environment.get_env(environment.SLACK_API_BASE_URL)
    url = f'{api_base_url}/files.upload'
    #headers = {'Content-type': 'multipart/form-data'}
    headers = {}
    payload = get_payload(channel, deployment, report_path, box_link)
    files = {'file': (report_path, open(report_path, 'rb'), 'binary')}
    LOG.debug('File upload payload is: "%s"', payload)
    LOG.debug('File data is: "%s"', files)
    try:
        LOG.debug('Calling Slack with payload "%s"', payload)
        response = requests.post(url, files=files, data=payload, headers=headers)
        LOG.debug('Response was "%s"', response.text)
    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not send slack notification to channel "%s": "%s"',
                  channel, request_ex)

def get_payload(channel, deployment, report_path, box_link):
    slack_token = environment.get_env(environment.SLACK_TOKEN)
    app_name = deployment_util.get_application_name(deployment)
    app_version = deployment_util.get_application_version(deployment)
    app_url = deployment_util.get_full_application_url(deployment)
    return {
        'filename': create_file_name(deployment),
        'token': slack_token,
        'channels': channel,
        'filetype': 'binary',
        'title': f'Lighthouse report for application {app_name}:{app_version}',
        'initial_comment': (f'This report was created by scanning {app_url} and the total '
                            'score for this report was {0:.2f}/5.0. Link to report in box is {}'
                            .format(parse_total_score(report_path), box_link))
    }

def create_file_name(deployment):
    cluster_name = deployment_util.get_cluster(deployment)
    app_name = deployment_util.get_application_name(deployment)
    date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    return f'report_{app_name}_{cluster_name}_{date_time}.html'

def parse_total_score(report_path):
    total_score = 0.0
    with open(report_path, 'r') as report_file:
        content = report_file.read()
        total_score += get_score(r'"id":"accessibility","score":(.+?)}', content)
        total_score += get_score(r'"id":"performance","score":(.+?)}', content)
        total_score += get_score(r'"id":"pwa","score":(.+?)}', content)
        total_score += get_score(r'"id":"best-practices","score":(.+?)}', content)
        total_score += get_score(r'"id":"seo","score":(.+?)}', content)
    return total_score

def get_score(pattern, content):
    value = re.search(pattern, content)
    if value:
        try:
            return float(value.group(1))
        except ValueError:
            return 0
    return 0
