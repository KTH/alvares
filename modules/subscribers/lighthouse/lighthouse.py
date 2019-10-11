__author__ = 'tinglev'

import os
import re
import json
import shutil
import logging
import tempfile
import datetime
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from boxsdk import JWTAuth
from boxsdk import Client as BoxClient
from modules import environment
from modules.subscribers.slack import slack_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import deployment_util, process

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    logger = logging.getLogger(__name__)
    if not deployment_util.get_test_accessibility(deployment):
        logger.debug('testAccessibility not set - skipping Lighthouse')
        return deployment
    if not environment.get_env(environment.SLACK_TOKEN):
        logger.info('No SLACK_TOKEN env provided. Cant run lighthouse')
        return deployment
    urls_to_scan = get_urls_to_scan(deployment)
    if urls_to_scan:
        for scan_url in urls_to_scan:
            process_url_to_scan(deployment, scan_url)
    return deployment

def process_url_to_scan(deployment, url_to_scan):
    logger = logging.getLogger(__name__)
    try:
        tmp_dir = tempfile.mkdtemp()
        logger.debug('Temp dir created, running headless-lighthouse')
        image = environment.get_env(environment.LIGHTHOUSE_IMAGE)
        output = process.run_with_output(f'docker run -e URL={url_to_scan} '
                                         f'-v {tmp_dir}:/report '
                                         f'{image}')
        logger.debug('Output from lighthouse was: "%s"', output)
        report_path = f'{tmp_dir}/report.html'
        #box_link = upload_to_box(report_path, deployment)
        for channel in slack_util.get_deployment_channels(deployment):
            send_file_to_slack(channel, deployment, report_path, url_to_scan)
    finally:
        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

def get_urls_to_scan(deployment):
    explicit_urls = deployment_util.get_accessibility_urls(deployment)
    if explicit_urls:
        return explicit_urls
    else:
        return [deployment_util.get_application_url(deployment)]

def upload_to_box(report_path, deployment):
    box_auth_string = environment.get_env(environment.BOX_AUTH_JSON)
    box_auth_json = json.loads(box_auth_string.replace("'", ""))
    box_sdk = JWTAuth.from_settings_dictionary(box_auth_json)
    client = BoxClient(box_sdk)
    file_name = create_file_name(deployment)
    # Folder id 0 is the root folder
    box_file = client.folder('0').upload(report_path, file_name)
    return box_file.get_shared_link(access='open')

def send_file_to_slack(channel, deployment, report_path, scanned_url):
    logger = logging.getLogger(__name__)
    logger.debug('Starting upload of lighthouse report to Slack')
    api_base_url = environment.get_env(environment.SLACK_API_BASE_URL)
    api_url = f'{api_base_url}/files.upload'
    #headers = {'Content-type': 'multipart/form-data'}
    headers = {}
    payload = get_payload(channel, deployment, report_path, scanned_url)
    files = {'file': (report_path, open(report_path, 'rb'), 'binary')}
    logger.debug('File upload payload is: "%s"', payload)
    logger.debug('File data is: "%s"', files)
    try:
        logger.debug('Calling Slack with payload "%s"', payload)
        response = requests.post(api_url, files=files, data=payload, headers=headers)
        logger.debug('Response was "%s"', response.text)
    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        logger.error('Could not send slack lighthouse notification to channel "%s": "%s"',
                  channel, request_ex)

def get_payload(channel, deployment, report_path, scanned_url):
    slack_token = environment.get_env(environment.SLACK_TOKEN)
    return {
        'filename': create_file_name(deployment),
        'token': slack_token,
        "username": "Accessibility testing report from Google Lighthouse",
        'channels': channel,
        'filetype': 'binary',
        'initial_comment': '{0:.2f}/4.0 | Accessibility report for {}'.format(
                parse_total_score(report_path),
                deployment_util.get_friendly_name(deployment)),
        'title': (f'This report was created by scanning {scanned_url}')
    }

def create_file_name(deployment):
    cluster_name = deployment_util.get_cluster(deployment)
    app_name = deployment_util.get_application_name(deployment)
    date_time = get_current_date_time()
    return f'report_{app_name}_{cluster_name}_{date_time}.html'

def get_current_date_time():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')

def parse_total_score(report_path):
    total_score = 0.0
    with open(report_path, 'r') as report_file:
        content = report_file.read()
        total_score += get_score(r'"id":"accessibility","score":(.+?)}', content)
        total_score += get_score(r'"id":"performance","score":(.+?)}', content)
        #total_score += get_score(r'"id":"pwa","score":(.+?)}', content)
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
