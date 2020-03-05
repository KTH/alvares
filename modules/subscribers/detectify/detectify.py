__author__ = 'tinglev'

import logging
import json
from requests import get, post, HTTPError, ConnectTimeout, RequestException
from modules import environment
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import deployment_util

LOG = logging.getLogger(__name__)

class DetectifyError(Exception):
    pass

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    if should_use_cluster(deployment):
        for api_key in environment.get_env_list(environment.DETECTIFY_API_KEYS):
            try:
                process_api_key(api_key, deployment)
            except DetectifyError:
                continue
    return deployment

def should_use_cluster(deployment):
    global LOG # pylint: disable=W0603
    cluster_ok = (deployment_util.get_cluster(deployment) in
                  environment.get_env_list(environment.DETECTIFY_CLUSTERS))
    if not cluster_ok:
        LOG.debug('Cluster "%s" not in DETECTIFY_CLUSTERS, skipping Detectify integration',
                  deployment_util.get_cluster(deployment))
    return cluster_ok

def process_api_key(api_key, deployment):
    global LOG # pylint: disable=W0603
    auth_header = create_auth_header(api_key)
    scan_list_json = get_scan_list_json(auth_header)
    token_list = get_token_list_from_json(scan_list_json)
    if not deployment_util.get_detectify_tokens(deployment):
        LOG.info('No Detectify profile tokens found for deployment, skipping')
        return
    for token in deployment_util.get_detectify_tokens(deployment):
        try:
            process_profile_token(token, token_list, auth_header)
        except DetectifyError:
            continue

def process_profile_token(token, token_list, auth_header):
    if token in token_list:
        scan_state = get_scan_state(auth_header, token)
        evaluate_scan_state(auth_header, scan_state, token)

def evaluate_scan_state(auth_header, scan_state, token):
    global LOG # pylint: disable=W0603
    if scan_state == 'stopped':
        start_scan(auth_header, token)
    else:
        LOG.info('Detectify not started. Scan already active with state "%s"',
                 scan_state)

def start_scan(auth_header, token):
    scan_endpoint = create_scan_start_url(token)
    response = call_detectify_endpoint(scan_endpoint, auth_header, post)
    raise_if_not_200(response)

def raise_if_not_200(response):
    global LOG # pylint: disable=W0603
    error = None
    if not response:
        error = 'HTTP error while getting scan status'
    else:
        codes = {
            400: 'Malformed scan profile token',
            401: 'Invalid API key',
            403: 'The provided API key cannot access this functionality',
            404: 'Valid scan profile token provided, but not found',
            409: 'Scan already running for profile',
            423: 'Locked. The domain is not verified',
            500: f'Internal Detectify server error: "{response}"',
            502: f'Internal Detectify server error: "{response}"',
            503: f'Internal Detectify server error: "{response}"',
            504: f'Internal Detectify server error: "{response}"'
        }
        error = codes.get(response.status_code, None)
    if error:
        LOG.error(error)
        raise DetectifyError(error)

def get_scan_state(auth_header, token):
    global LOG # pylint: disable=W0603
    status_endpoint = create_scan_status_url(token)
    LOG.debug('Calling detectify endpoint')
    status_response = call_detectify_endpoint(status_endpoint, auth_header, get)
    raise_if_not_200(status_response)
    LOG.debug('Got scan status code response from detectify: "%s"',
              status_response)
    # This should be ['status'] according to documentation, but it's returning
    # ['state'], so we're using that
    return json.loads(status_response.text)['state']

def get_scan_list_json(auth_header):
    list_endpoint = create_profile_list_url()
    list_response = call_detectify_endpoint(list_endpoint, auth_header, get)
    raise_if_not_200(list_response)
    return json.loads(list_response.text)

def get_token_list_from_json(profile_list):
    return [token['token'] for token in profile_list]

def create_scan_status_url(token):
    return ('https://api.detectify.com/rest/v2/scans/{0}/'
            .format(token))

def create_scan_start_url(token):
    return ('https://api.detectify.com/rest/v2/scans/{0}/'
            .format(token))

def create_profile_list_url():
    return 'https://api.detectify.com/rest/v2/profiles/'

def create_auth_header(api_key):
    return {'X-Detectify-Key': api_key}

def call_detectify_endpoint(url, auth_header, method):
    global LOG # pylint: disable=W0603
    try:
        LOG.debug('Calling Detectify at url "%s" with auth "%s"', url, auth_header)
        response = method(url, headers=auth_header)
        LOG.debug('Response was "%s"', response.text)
        return response

    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not call Detectify endpoint "%s": "%s"',
                  url, request_ex)
        raise DetectifyError('HTTP error while calling Detectify')
