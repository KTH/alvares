__author__ = 'tinglev'

import logging
import threading
from flask import Flask, request, abort
from modules.event_system import event_system
from modules.subscribers.slack import (slack_deployment, slack_error,
                                       slack_recommendation)
from modules.subscribers.detectify import detectify
from modules.subscribers.database import cosmosdb
from modules.subscribers.uptimerobot import uptimerobot
from modules.subscribers.application_endpoint import application_endpoint
from modules.subscribers.lighthouse import lighthouse
from modules.log import init_logging
from modules import deployment_util
from modules import deployment_enricher

FLASK = Flask(__name__)

def fire_event(event, event_data):
    event_system.publish_event(event, event_data)

def fire_event_in_thread(event, event_data):
    event_thread = threading.Thread(target=fire_event, args=(event, event_data,))
    event_thread.start()

def init_subscriptions():
    subscribers = [cosmosdb, detectify, slack_deployment, slack_error,
                   slack_recommendation, uptimerobot, application_endpoint,
                   lighthouse]
    event_system.init_subscriptions(subscribers)

@FLASK.before_request
def only_accept_json_requests():
    if not request.is_json:
        abort(400)

@FLASK.route('/api/v1/deployment', methods=['PUT'])
def new_deployment():
    log = logging.getLogger(__name__)
    deployment = request.get_json()
    log.debug('Raw deployment: "%s"', deployment)
    deployment = deployment_enricher.enrich(deployment)
    log.debug('Deployment with default values: "%s"', deployment)

    fire_event_in_thread('deployment', deployment)
    
    return '200 OK'

@FLASK.route('/api/v1/error', methods=['PUT'])
def new_error():
    log = logging.getLogger(__name__)
    error = request.get_json()
    log.debug('Got error: "%s"', error)
    fire_event_in_thread('error', error)
    return '200 OK'

@FLASK.route('/api/v1/recommendation', methods=['PUT'])
def new_recommendation():
    recommendation = request.get_json()
    fire_event_in_thread('recommendation', recommendation)
    return '200 OK'

#
# Start server
#

def start_server():
    init_logging()
    log = logging.getLogger(__name__)
    log.info('Starting application')
    init_subscriptions()
    FLASK.run(host='0.0.0.0', port=3010, debug=False)

if __name__ == '__main__':
    start_server()
