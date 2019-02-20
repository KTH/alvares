import logging
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import environment
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors

# Docs:
# https://github.com/Azure/azure-cosmos-python/blob/a21f6fb4bad3f59909ef43558b598f9fb476b7bc/samples/DatabaseManagement/Program.py

LOG = logging.getLogger(__name__)

DATABASE_ID = 'dizin'
DATABASE_LINK = 'dbs/' + DATABASE_ID
CONTAINER_ID = 'applications'


def subscribe():
    subscribe_to_event('deployment', handle_deployment)


def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)


def handle_deployment(deployment):

    LOG.info('Started process of writing to dizin/applications.')
    client = get_client()

    document = save(client, get_container(client, get_database(client)), deployment)

    if not document:
        LOG.error("Could not store the deployment in '%s'.", CONTAINER_ID)
    else:
        LOG.debug("Wrote document to dizin/applications. '%s'.", document)

    return deployment


# 
# Gets a client to CosmosDB in Azure.
#
def get_client():
    result = None

    result = cosmos_client.CosmosClient(
        url_connection=environment.get_env(environment.DB_URL),
        auth={'masterKey': environment.get_env(environment.DB_PASSWORD)}
    )

    return result


#
# Creates a new database, or returns an already existing one.
#
def create_database(client):

    result = None

    try:

        result = client.CreateDatabase({'id': DATABASE_ID})
        LOG.info("Created a database with database id '%s'.", DATABASE_ID)

    except errors.HTTPFailure as http_failure:
        if http_failure.status_code == 409:
            LOG.debug("Database with id '%s' already created.", DATABASE_ID)
            result = get_database(client)
        else:
            raise errors.HTTPFailure(http_failure.status_code)

    return result


#
# Get the database to store containers (collections) in.
# If no database is found a new is created.
#
def get_database(client):

    result = None

    try:

        result = client.ReadDatabase(DATABASE_LINK)
        LOG.debug("Database with id '%s' was found, its _self is '%s'",
                  DATABASE_ID, result['_self'])

    except errors.HTTPFailure as http_failure:
        if http_failure.status_code == 404:
            LOG.debug("A database with id %s does not exist", DATABASE_ID)
            result = create_database(client)
        else:
            raise errors.HTTPFailure(http_failure.status_code)

    return result


#
# Creates a new container, or returns an already existing one.
#
def create_container(client, database):

    result = None

    try:

        result = client.CreateContainer(
            database['_self'],
            {'id': CONTAINER_ID},
            {'offerThroughput': 400}
        )
        LOG.info("Created a container with container id '%s'.", CONTAINER_ID)

    except errors.HTTPFailure as http_failure:
        if http_failure.status_code == 409:
            LOG.debug("A collection with id '%s' already exists.", CONTAINER_ID)
            result = get_container(client, database)
        else:
            raise errors.HTTPFailure(http_failure.status_code)

    return result


#
# Get the container to store documents in.
# If no container is found a new is created.
#
def get_container(client, database):

    result = None

    try:

        collection_link = DATABASE_LINK + '/colls/{0}'.format(CONTAINER_ID)
        result = client.ReadContainer(collection_link)
        LOG.debug("Got a collection with collection link '%s'.", collection_link)

    except errors.HTTPFailure as http_failure:
        if http_failure.status_code == 404:
            LOG.info("A collection with id '%s' does not exist", CONTAINER_ID)
            result = create_container(client, database)
        else:
            raise errors.HTTPFailure(http_failure.status_code)

    return result


#
# Save a deployment as a json document.
#
def save(client, container, deployment):
    return client.CreateItem(container['_self'], deployment)