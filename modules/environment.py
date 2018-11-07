import os

DEBUG = 'DEBUG'
UTR_CLUSTERS = 'UTR_CLUSTERS'
UTR_EXCLUDED_APPS = 'UTR_EXCLUDED_APPS'

UTR_KTH_APP_HOST = 'UTR_KTH_APP_HOST'
UTR_KTH_API_HOST = 'UTR_KTH_API_HOST'
UTR_KTH_APP_HOST_STAGE = 'UTR_KTH_APP_HOST_STAGE'
UTR_KTH_API_HOST_STAGE = 'UTR_KTH_API_HOST_STAGE'
UPTIMEROBOT_API_KEY = 'UPTIMEROBOT_API_KEY'
DB_URL = 'DB_URL'
DB_PASSWORD = 'DB_PASSWORD'
DETECTIFY_API_KEYS = 'DETECTIFY_API_KEYS'
DETECTIFY_CLUSTERS = 'DETECTIFY_CLUSTERS'

SLACK_CHANNEL_OVERRIDE = 'SLACK_CHANNEL_OVERRIDE'
SLACK_CHANNELS = 'SLACK_CHANNELS'
SLACK_WEB_HOOK = 'SLACK_WEB_HOOK'
DISABLED_SUBSCRIBERS = 'DISABLED_SUBSCRIBERS'
SKIP_VALIDATION_TESTS = 'SKIP_VALIDATION_TESTS'
VALIDATE_DEPLOYMENT_URL = 'VALIDATE_DEPLOYMENT_URL'
UTR_API_BASE_URL = 'UTR_API_BASE_URL'
UTR_API_KEY = 'UTR_API_KEY'
UTR_KEYWORD = 'UTR_KEYWORD'
ACTIVE_APP_HOST = 'ACTIVE_APP_HOST'
ACTIVE_API_HOST = 'ACTIVE_API_HOST'
STAGE_APP_HOST = 'STAGE_APP_HOST'
STAGE_API_HOST = 'STAGE_API_HOST'
GRAYLOG_HOST = 'GRAYLOG_HOST'

def get_env(name):
    return os.environ.get(name)

def get_env_list(name):
    if os.environ.get(name):
        return [ch.rstrip() for ch in os.environ.get(name).split(',')]
    return []

def get_env_with_default_value(name, default_value):
    value = os.environ.get(name)
    if not value:
        return default_value
    return value

def use_debug(): # pragma: no cover
    return os.environ.get(DEBUG)

def get_utr_clusters():
    clusters = os.environ.get(UTR_CLUSTERS)
    return [cluster.rstrip() for cluster in clusters.split(',')]

def get_utr_excluded_apps():
    excluded_apps = os.environ.get(UTR_EXCLUDED_APPS)
    return [app.rstrip() for app in excluded_apps.split(',')]

def get_app_host(cluster_name):
    if cluster_name == "stage":
        if os.environ.get(UTR_KTH_APP_HOST_STAGE):
            return os.environ.get(UTR_KTH_APP_HOST_STAGE)
        return "https://app-r.referens.sys.kth.se"
    else:
        if os.environ.get(UTR_KTH_APP_HOST):
            return os.environ.get(UTR_KTH_APP_HOST)
        return "https://app.kth.se"

def get_api_host(cluster_name):
    if cluster_name == "stage":
        if os.environ.get(UTR_KTH_API_HOST_STAGE):
            return os.environ.get(UTR_KTH_API_HOST_STAGE)
        return "https://api-r.referens.sys.kth.se"
    else:
        if os.environ.get(UTR_KTH_API_HOST):
            return os.environ.get(UTR_KTH_API_HOST)
        return "https://api.kth.se"


def get_utr_kth_app_host():
    if os.environ.get(UTR_KTH_APP_HOST):
        return os.environ.get(UTR_KTH_APP_HOST)
    return "https://app.kth.se"

def get_utr_kth_api_host():
    if os.environ.get(UTR_KTH_API_HOST):
        return os.environ.get(UTR_KTH_API_HOST)
    return "https://api.kth.se"
