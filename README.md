# alvares

API to handle integrations or different sorts. Handles successful deployments to the CD environment aswell as errors and label recommendations.

### How it works
Alvares gets a json from the deployment process Aspen with information about any deployments it has just done into a cluster.

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

_Example: deployment data from Aspen sent to Alvares

When Alvares recives the deployemnt data it enriches this with more data
(like url:s) and then sends the enriched deployement json to all integrations to do there thing.

### Integrations
- *Slack* Extended developer information about the deployment
- *Dizin database* Stores deployments for Flottsbro-API
- *Detectify* Security scanning
- *Lighthouse* A18y scanning
- *UptimeRobot* Monitoring public urls, also the source for Nagios monitoring

## Add your own integration

1) Create a module under /subscribers
2) Make sure the module has the two methods `subscribe()` and `unsubscribe()`
3) Add the module to the `init_subscriptions()` method in `run.py`

## Skip certain integrations

To skip an integration, just set the environment variable `DISABLED_SUBSCRIBERS` to a comma
separated list of all module names that should be excluded. For example:
`modules.subscribers.database.cosmosdb`
