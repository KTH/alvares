__author__ = 'tinglev@kth.se'

from modules.event_system.event_system import subscribe_to_event, unsubscribe_from_event

def subscribe():
    subscribe_to_event('deployment', handle_deployment)
    subscribe_to_event('error', handle_error)
    subscribe_to_event('recommendation', handle_recommendation)

def unsubscribe():
    unsubscribe_from_event('deployment', handle_error)
    unsubscribe_from_event('error', handle_error)
    unsubscribe_from_event('recommendation', handle_recommendation)

def handle_deployment(data):
    pass

def handle_error(data):
    pass

def handle_recommendation(data):
    pass
