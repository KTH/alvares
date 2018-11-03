__author__ = 'tinglev'

import logging
from flask import Flask, request, abort
from modules.event_system.event_system import publish_event
from modules.subscribers import slack
from modules.log import init_logging

FLASK = Flask(__name__)

def init_subscriptions():
    slack.subscribe()

@FLASK.before_request
def only_accept_json_requests():
    if not request.is_json:
        abort(400)

@FLASK.route('/api/v1/deployment', methods=['PUT'])
def new_deployment():
    deployment = request.json()
    publish_event('deployment', deployment)

@FLASK.route('/api/v1/error', methods=['PUT'])
def new_error():
    error = request.json()
    publish_event('error', error)

@FLASK.route('/api/v1/recommendation', methods=['PUT'])
def new_recommendation():
    recommendation = request.json()
    publish_event('recommendation', recommendation)

#
# Start server
#

if __name__ == '__main__':
    init_logging()
    log = logging.getLogger(__name__)
    log.info('Starting application')
    init_subscriptions()
    FLASK.run(host='0.0.0.0', port=3010, debug=False)
