__author__ = 'tinglev'

import logging
import pydocumentdb.document_client as docdb_client
import pydocumentdb.errors as docdb_errors
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event
from modules import environment

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('deployment', handle_deployment)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_deployment)

def handle_deployment(deployment):
    client = connect_to_db()
    database = create_database(client)
    collections = create_collections(client, database)
    write_deployment(client, collections['deployments'], deployment)
     write_deployment(client, collections['applications'], deployment)
    return deployment

def connect_to_db():
    global LOG # pylint: disable=W0603
    try:
        LOG.debug('Connecting to Azure document db')
        return docdb_client.DocumentClient(
            environment.get_env(environment.DB_URL),
            {'masterKey': environment.get_env(environment.DB_PASSWORD)}
        )
    except docdb_errors.DocumentDBError as db_e:
        raise Exception('Failed to connect to the Azure documentdb. '
                        'Error was: "{}"'.format(db_e), db_e)

def create_database(client):
    global LOG # pylint: disable=W0603
    try:
        LOG.debug('Creating database "dizin"')
        return client.CreateDatabase({'id': 'dizin'})
    except docdb_errors.DocumentDBError as db_err:
        return handle_database_error(client, db_err)

def handle_database_error(client, db_err):
    global LOG # pylint: disable=W0603
    if db_err.status_code == 409:
        LOG.debug('A database with id "dizin" already exists')
        return get_existing_database(client)
    else:
        raise Exception('Error when creating database', db_err)

def get_existing_database(client):
    try:
        query = {'query': 'SELECT * FROM d WHERE d.id = "dizin"'}
        options = {'maxItemCount': 1}
        return list(client.QueryDatabases(query, options))[0]
    except docdb_errors.DocumentDBError as query_err:
        raise Exception('Error while querying for database "dizin"',
                        query_err)

def create_collections(client, database):
    global LOG # pylint: disable=W0603
    collections = {}
    for collection_name in ['deployments', 'errors', 'applications']:
        try:
            LOG.debug('Creating collection "%s"', collection_name)
            collections[collection_name] = client.CreateCollection(database['_self'],
                                                                   {'id': collection_name})
        except docdb_errors.DocumentDBError as coll_ex:
            collections[collection_name] = handle_collection_error(client,
                                                                   database,
                                                                   collection_name,
                                                                   coll_ex)
        return collections

def handle_collection_error(client, database, collection_name, ex):
    global LOG # pylint: disable=W0603
    if ex.status_code == 409:
        LOG.debug('A collection with id "%s" already exists', collection_name)
        return get_existing_collection(client, database, collection_name)
    else:
        raise Exception('Error when creating collection "{}"'
                        .format(collection_name), ex)

def get_existing_collection(client, database, collection_name):
    try:
        query = {'query': 'SELECT * FROM c WHERE c.id = "{}"'.format(collection_name)}
        options = {'maxItemCount': 1}
        return list(client.QueryCollections(database['_self'],
                                            query, options))[0]
    except docdb_errors.DocumentDBError as query_err:
        raise Exception('Error while querying for collection "{}"'
                        .format(collection_name), query_err)

def write_deployment(client, collection, deployment):
    global LOG # pylint: disable=W0603
    try:
        LOG.info('Writing deployment "%s"', deployment)
        client.CreateDocument(collection['_self'], deployment)
    except docdb_errors.DocumentDBError as doc_err:
        raise Exception('Error when saving application to database', doc_err)
