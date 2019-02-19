import logging
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import environment
import azure.cosmos.cosmos_client as cosmos_client

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    LOG.info('Started process of writing to dizin/applications.')
    client = get_client()

    document = save(client, create_container(client, create_database(client)), deployment)
    LOG.info('Wrote document to dizin/applications.')
    return deployment

def get_client():
    return cosmos_client.CosmosClient(
        url_connection=environment.get_env(environment.DB_URL),
        auth={'masterKey': environment.get_env(environment.DB_PASSWORD)}
    )

def create_database(client):
    return client.CreateDatabase({'id': 'dizin'})

def create_container(client, database):
    return client.CreateContainer(
        database['_self'],
        {'id': 'applications'},
        {'offerThroughput': 400}
    )

def save(client, container, deployment):
    document = client.CreateItem(container['_self'], deployment)
    return document
