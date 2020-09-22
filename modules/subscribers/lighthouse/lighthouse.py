__author__ = 'tinglev'

import os
from os import environ
import re
import json
import shutil
import logging
import tempfile
from urllib.parse import urlparse
from datetime import datetime
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from boxsdk import JWTAuth
from boxsdk import Client as BoxClient
from azure.storage.blob import BlobServiceClient, BlobProperties, ContentSettings
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
        app_name = deployment_util.get_application_name(deployment)
        commit = deployment_util.get_application_version(deployment)
        commit = commit.split('_')[1]
        url_path = urlparse(url_to_scan).path.replace('/', '-')
        report_path = f'{tmp_dir}/{app_name}_{commit}_{url_path}'
        os.rename(f'{tmp_dir}/report.report.html', f'{report_path}.html')
        os.rename(f'{tmp_dir}/report.report.json', f'{report_path}.json')

        logger.debug(f'Report path is {report_path}.html')
        #box_link = upload_to_box(report_path, deployment)
        for channel in slack_util.get_deployment_channels(deployment):
            send_file_to_slack(channel, deployment, f'{report_path}.html', url_to_scan)
        if environment.get_env(environment.LIGHTHOUSE_STORAGE_CONN_STRING):
            upload_to_storage(deployment, report_path, url_path)
    finally:
        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

def upload_to_storage(deployment, report_path, url_path):
    logger = logging.getLogger(__name__)
    logger.info('Lighthouse connections string found, uploading report')
    connect_str = environment.get_env(environment.LIGHTHOUSE_STORAGE_CONN_STRING)
    client = BlobServiceClient.from_connection_string(connect_str)
    container = 'no team'
    if 'team' in deployment:
        container = deployment['team']
    try:
        logger.debug(f'Using container "{container}"')
        client.create_container(container)
    except:
        logger.debug('Container already exists')
    clean_old_blobs(deployment, client, container, url_path)
    html_path = f'{report_path}.html'
    json_path = f'{report_path}.json'
    filename = os.path.basename(html_path)
    blob_properties = get_blob_properties(filename)
    blob_client = client.get_blob_client(container=container, blob=blob_properties)
    with open(html_path, "rb") as data:
        try:
            blob_client.upload_blob(data)
        except:
            logger.debug('Couldnt upload file. Does it already exist?')
    filename = os.path.basename(json_path)
    blob_properties = get_blob_properties(filename)
    blob_client = client.get_blob_client(container=container, blob=blob_properties)
    with open(json_path, "rb") as data:
        try:
            blob_client.upload_blob(data)
        except:
            logger.debug('Couldnt upload file. Does it already exist?')
    logger.info('Report upload complete')

def get_blob_properties(filename):
    props = BlobProperties()
    content = ContentSettings()
    if '.json' in filename:
        content.content_type = 'application/json'
    elif '.html' in filename:
        content.content_type = 'text/html'
    else:
        content.content_type = 'text/plain'
    content.content_disposition = f'attachment; filename={filename}'
    props.content_settings = content
    return props

def clean_old_blobs(deployment, service_client, container_name, url_path):
    logger = logging.getLogger(__name__)
    client = service_client.get_container_client(container_name)
    app_name = deployment_util.get_application_name(deployment)
    blobs = client.list_blobs(name_starts_with=app_name)
    as_list = [
        b for b 
        in blobs 
        if b.name.replace('.html', '').replace('.json', '').endswith(url_path)
    ]
    as_list.sort(key=lambda b:b.last_modified, reverse=True)
    max_files_per_path = 10
    if len(as_list) > max_files_per_path:
        logger.info(f'Cleaning {len(as_list) - max_files_per_path} old reports')
        for b in as_list[max_files_per_path:]:
            blob_client = service_client.get_blob_client(
                container=container_name,
                blob=b.name
            )
            blob_client.delete_blob()

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
        'initial_comment': f'Google Lighthouse accessibility report {deployment_util.get_friendly_name(deployment)}.',
        'title': (f'Score for {scanned_url}: {0:.2f}/4.0'.format(parse_total_score(report_path)))
    }

def create_file_name(deployment):
    cluster_name = deployment_util.get_cluster(deployment)
    app_name = deployment_util.get_application_name(deployment)
    date_time = get_current_date_time()
    return f'report_{app_name}_{cluster_name}_{date_time}.html'

def get_current_date_time():
    return datetime.now().strftime('%Y-%m-%d_%H-%M')

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
