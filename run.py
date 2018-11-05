__author__ = 'tinglev'

import logging
from flask import Flask, request, abort
from modules.event_system import event_system
from modules.subscribers.slack import (slack_deployment, slack_error,
                                       slack_recommendation)
from modules.subscribers.detectify import detectify
from modules.subscribers.database import database
from modules.subscribers.uptimerobot import uptimerobot
from modules.log import init_logging

FLASK = Flask(__name__)

def init_subscriptions():
    subscribers = [database, detectify, slack_deployment, slack_error,
                   slack_recommendation, uptimerobot]
    event_system.init_subscriptions(subscribers)

@FLASK.before_request
def only_accept_json_requests():
    if not request.is_json:
        abort(400)

@FLASK.route('/api/v1/deployment', methods=['PUT'])
def new_deployment():
    deployment = request.json()
    event_system.publish_event('deployment', deployment)

@FLASK.route('/api/v1/error', methods=['PUT'])
def new_error():
    error = request.json()
    event_system.publish_event('error', error)

@FLASK.route('/api/v1/recommendation', methods=['PUT'])
def new_recommendation():
    recommendation = request.json()
    event_system.publish_event('recommendation', recommendation)

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
