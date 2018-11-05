__author__ = 'tinglev@kth.se'

import logging
from modules import environment
from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event

LOG = logging.getLogger(__name__)

def subscribe():
    subscribe_to_event('recommendation', handle_recommendation)

def unsubscribe():
    unsubscribe_from_event('recommendation', handle_recommendation)

def handle_recommendation(recommendation):
    pass
