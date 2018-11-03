import os

ENV_DEBUG = 'DEBUG'
ENV_DRY_RUN = 'DRY_RUN'
ENV_UTR_CLUSTERS = 'UTR_CLUSTERS'
ENV_UTR_EXCLUDED_APPS = 'UTR_EXCLUDED_APPS'
ENV_SLACK_CHANNELS = 'SLACK_CHANNELS'
ENV_UTR_KTH_APP_HOST = 'UTR_KTH_APP_HOST'
ENV_UTR_KTH_API_HOST = 'UTR_KTH_API_HOST'
ENV_UTR_KTH_APP_HOST_STAGE = 'UTR_KTH_APP_HOST_STAGE'
ENV_UTR_KTH_API_HOST_STAGE = 'UTR_KTH_API_HOST_STAGE'
ENV_UPTIMEROBOT_API_KEY = 'UPTIMEROBOT_API_KEY'
ENV_SLACK_WEB_HOOK = 'SLACK_WEB_HOOK_URL'
ENV_DB_URL = 'DB_URL'
ENV_DB_PASSWORD = 'DB_PASSWORD'
ENV_DETECTIFY_API_KEYS = 'DETECTIFY_API_KEYS'
ENV_DETECTIFY_CLUSTERS = 'DETECTIFY_CLUSTERS'
ENV_SLACK_CHANNEL_OVERRIDE = 'SLACK_CHANNEL_OVERRIDE'

def use_debug(): # pragma: no cover
    return os.environ.get(ENV_DEBUG)

def is_dry_run(): # pragma: no cover
    return os.environ.get(ENV_DRY_RUN)

def get_utr_clusters():
    clusters = os.environ.get(ENV_UTR_CLUSTERS)
    return [cluster.rstrip() for cluster in clusters.split(',')]

def get_utr_excluded_apps():
    excluded_apps = os.environ.get(ENV_UTR_EXCLUDED_APPS)
    return [app.rstrip() for app in excluded_apps.split(',')]

def get_slack_channels():
    channels = os.environ.get(ENV_SLACK_CHANNELS)
    return [channel.rstrip() for channel in channels.split(',')]

def get_slack_web_hook():
    return os.environ.get(ENV_SLACK_WEB_HOOK)

def get_app_host(cluster_name):
    if cluster_name == "stage":
        if os.environ.get(ENV_UTR_KTH_APP_HOST_STAGE):
            return os.environ.get(ENV_UTR_KTH_APP_HOST_STAGE)
        return "https://app-r.referens.sys.kth.se"
    else:
        if os.environ.get(ENV_UTR_KTH_APP_HOST):
            return os.environ.get(ENV_UTR_KTH_APP_HOST)
        return "https://app.kth.se"

def get_api_host(cluster_name):
    if cluster_name == "stage":
        if os.environ.get(ENV_UTR_KTH_API_HOST_STAGE):
            return os.environ.get(ENV_UTR_KTH_API_HOST_STAGE)
        return "https://api-r.referens.sys.kth.se"
    else:
        if os.environ.get(ENV_UTR_KTH_API_HOST):
            return os.environ.get(ENV_UTR_KTH_API_HOST)
        return "https://api.kth.se"


def get_utr_kth_app_host():
    if os.environ.get(ENV_UTR_KTH_APP_HOST):
        return os.environ.get(ENV_UTR_KTH_APP_HOST)
    return "https://app.kth.se"

def get_utr_kth_api_host():
    if os.environ.get(ENV_UTR_KTH_API_HOST):
        return os.environ.get(ENV_UTR_KTH_API_HOST)
    return "https://api.kth.se"

def get_utr_api_key():
    return os.environ.get(ENV_UPTIMEROBOT_API_KEY)

def get_db_url():
    return os.environ.get(ENV_DB_URL)

def get_db_password():
    return os.environ.get(ENV_DB_PASSWORD)

def get_slack_channel_override():
    return os.environ.get(ENV_SLACK_CHANNEL_OVERRIDE)

def get_detectify_clusters():
    clusters = os.environ.get(ENV_DETECTIFY_CLUSTERS)
    return [cluster.rstrip() for cluster in clusters.split(',')]

def get_detectify_api_keys():
    keys = os.environ.get(ENV_DETECTIFY_API_KEYS)
    return [key.rstrip() for key in keys.split(',')]
