# alvares

API to handle integrations or different sorts. Handles successful deployments to the CD environment aswell as errors and label recommendations.

## Add your own integration

1) Create a module under /subscribers
2) Make sure the module has the two methods `subscribe()` and `unsubscribe()`
3) Add the module to the `init_subscriptions()` method in `run.py`

## Skip certain integrations

To skip an integration, just set the environment variable `DISABLED_SUBSCRIBERS` to a comma
separated list of all module names that should be excluded. For example:
`modules.subscribers.database.cosmosdb`
