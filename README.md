# Alvares :loudspeaker: ![alt text](https://api.travis-ci.org/KTH/alvares.svg?branch=master)


External service integration API. Handles deployments, errors and recommendations from [Aspen](https://github.com/KTH/aspen) through a subscriber based module system.

## How to run

`docker build -t alvares . && docker run alvares`

## Run tests

`./run_tests.sh`

## Environment

| Name | Module | Description|
|------|--------|------------|
| DEBUG | All | Set to turn on DEBUG level logging |
| DISABLED_SUBSCRIBERS | All | List of subscribers to disable |
| SKIP_VALIDATION_TESTS | All | Skip validation tests when running test suite |
| VALIDATE_DEPLOYMENT_URL | All | URL to validation service for testing |
| ACTIVE_APP_HOST | All | Base host URL for the production web environment |
| ACTIVE_API_HOST | All | Base host URL for the production API environment |
| STAGE_APP_HOST | All | Base host URL for the stage web environment |
| STAGE_API_HOST | All | Base host URL for the stage API environment |
| INTEGRAL_APP_HOST | All | Base host URL for the production integral web environment |
| INTEGRAL_API_HOST | All | Base host URL for the production integral API environment |
| INTEGRAL_STAGE_APP_HOST | All | Base host URL for the stage integral web environment |
| INTEGRAL_STAGE_API_HOST | All | Base host URL for the stage integral API environment |
| GRAYLOG_HOST | All | Graylog host for log link creation |
| - | - | - |
| UTR_CLUSTERS | UpTimeRobot | Specify which clusters to monitor with UTR |
| UTR_EXCLUDED_APPS | UpTimeRobot | List of apps to exclude from UTR monitoring |
| UTR_KTH_APP_HOST | UpTimeRobot | Which public host to use for applications |
| UTR_KTH_API_HOST | UpTimeRobot | Which public host to use for API services |
| UTR_KTH_APP_HOST_STAGE | UpTimeRobot | Which stage host to use for applications |
| UTR_KTH_API_HOST_STAGE | UpTimeRobot | Which stage host to use for API services |
| UPTIMEROBOT_API_KEY | UpTimeRobot | UpTimeRobot API key to use |
| UTR_API_BASE_URL | UpTimeRobot | Base URL to UpTimeRobot API |
| UTR_API_KEY | UpTimeRobot | UpTimeRobot API key to use |
| UTR_KEYWORD | UpTimeRobot | Keyword to look for in monitored pages |
| - | - | - |
| DB_URL | Database | URL to databas |
| DB_PASSWORD | Database | Password to database |
| - | - | - |
| DETECTIFY_API_KEYS | Detectify | List of API keys to use |
| DETECTIFY_CLUSTERS | Detectify | Which clusters to perform Detectify scans on |
| - | - | - |
| SLACK_CHANNEL_OVERRIDE | Slack | Channel to send all Slack messages to, regardless of other configuration settings |
| SLACK_CHANNELS | Slack | List of channels to send messages to |
| SLACK_WEB_HOOK | Slack | The Slack webhook to use |
| SLACK_TOKEN | Slack | The Slack API token to use |
| SLACK_API_BASE_URL | Slack | The base URL for the Slack API to use |
| - | - | - |
| LIGHTHOUSE_IMAGE | Lighthouse | What Docker image of Lighthouse to use |
| - | - | - |
| FLOTTSBRO_API_KEY | Flottsbro | Key with scope write to Flottsbro |
| FLOTTSBRO_API_BASE_URL | Flottsbro | Protocoll and host to Flottsbro API |
| - | - | - |
| FEATURE_FLAG_LOFSDALEN | Lofsdalen | Turn on or off Lofsdalen |
| LOFSDALEN_API_BASE_URL | Lofsdalen | Protocoll and host to Lofsdalen API |

## How it works

Alvares gets a json object from the [Aspen](https://github.com/kth/aspen/) with information about any deployments or errors that have occured in the deployment pipeline. The object sent from Aspen looks something like this:

```json
{
    "applicationName": "kth-azure-app",
    "cluster": "active",
    "version": "2.0.11_abc123",
    "imageName": "kth-azure-app",
    "slackChannels": "#team-studadm,#developers",
    "publicNameSwedish": "Monitorapp",
    "publicNameEnglish": "Monitor application",
    "descriptionSwedish": "Monitorapp för klustret",
    "descriptionEnglish": "Monitor application for cluster",
    "created": "",
    "importance": "high",
    "applicationPath": "/kth-azure-app",
    "detectifyProfileTokens": "abc123xyz456,987mnb654vcx",
    "testAccessibility": "true"
}
```

When Alvares recives the deployment data it enriches this with more data
(like url:s) and then sends the enriched deployement json to all subscribing integration modules to do their thing.

## Integrations

- *Slack* - Extended developer information about the deployment
- *Dizin database* - Stores deployments for [Flottsbro-API](https://github.com/KTH/flottsbro-api)
- *Detectify* - Security scanning through APIs at [Detectify](https://detectify.com)
- *Lighthouse* - Accessability scanning through [Google Lighthouse](https://github.com/GoogleChrome/lighthouse)
- *UptimeRobot* - Health monitoring for public web endpoints through [UpTimeRobot](https://uptimerobot.com). Also serves as the source for our own Nagios monitoring.

## How to add a new integration

1) Create a module under /subscribers
2) Make sure the module has the two methods `subscribe()` and `unsubscribe()`
3) Add the module to the `init_subscriptions()` method in `run.py`

## Skip certain integrations

To skip an integration, just set the environment variable `DISABLED_SUBSCRIBERS` to a comma
separated list of all module names that should be excluded. For example:
`modules.subscribers.database.cosmosdb`
