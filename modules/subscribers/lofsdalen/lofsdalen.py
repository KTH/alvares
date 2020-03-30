__author__ = 'tinglev'
import logging
import requests
from requests import HTTPError, ConnectTimeout, RequestException
from modules import deployment_util
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules.subscribers.slack import slack_util
from modules import environment

LOG = logging.getLogger(__name__)

def get_base_url():
    return environment.get_env_with_default_value(environment.LOFSDALEN_API_BASE_URL, 'https://api-r.referens.sys.kth.se')

def get_repo_name(deployment):
    return deployment_util.get_image_name(deployment)

def get_commit(deployment):
    '''
    The version is in format "8.11.0_713eef5s", the last part is the git commit hash.
    '''
    version = deployment_util.get_application_version(deployment)
    return version[(version.find('_') + 1):]

def get_url(deployment):
    '''
    Make a url like:
    https://api-r.referens.sys.kth.se/api/lofsdalen/v1[/my-git-repo-name]/[commit-hash]/when
    i.e: https://api-r.referens.sys.kth.se/api/lofsdalen/v1/lofsdalen/4b1c21f/when
    '''
    return f"{get_base_url()}/api/lofsdalen/v1/{get_repo_name(deployment)}/{get_commit(deployment)}/when."

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    global LOG  # pylint: disable=W0603

    if environment.get_env_with_default_value('FEATURE_FLAG_LOFSDALEN', False):
        commited_when = call_lofsdalen_endpoint_when(get_url(deployment))
        if commited_when is not None:
            call_slack(deployment, commited_when)

    return deployment


def call_lofsdalen_endpoint_when(api_url):
    '''
    CalLS Lofsdalen and gets a json back about the commit date.
    {
    "commited": "2019-12-04T11:41:29Z",
    "commitedTimestamp": 1575459689,
    "nowTimestamp": 1585508436.723,
    "durationMs": 10048747.72300005,
    "readable": "4 months ago"
    }

    '''
    global LOG  # pylint: disable=W0603
    LOG.debug('Calling Lofsdalen for stats when a  "%s".', api_url,)
    try:

        response = requests.get(api_url)

        if response.status_code == 200:
            LOG.debug('Got commit information for "%s", got response was "%s"', api_url, response.text)
            return response.json()
        if response.status_code == 404:
            LOG.debug('Cound not find commit information for "%s", got response was "%s"', api_url, response.text)

    except (HTTPError, ConnectTimeout, RequestException) as request_ex:
        LOG.error('Could not call Lofsdalen: "%s"', request_ex)

    return None

def get_slack_text(commited_when):
    return f'This code was pushed to :github: Github *{commited_when["readable"]}*.'

def call_slack(deployment, commited_when):
    slack_util.call_slack_channels(deployment, get_slack_text(commited_when), "Git statistics (Alvares)")
