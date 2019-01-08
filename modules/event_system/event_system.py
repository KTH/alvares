__author__ = 'tinglev@kth.se'

import logging
from modules import environment

subscribers = {} # pylint: disable=C0103

def publish_event(event, data):
    logger = logging.getLogger(__name__)
    for function in get_all_event_functions(event):
        try:
            function(data)
        except Exception: # pylint: disable=W0703
            logger.exception('Caught exception when running subscription '
                             'function for a module.')

def get_all_event_functions(event):
    global subscribers # pylint: disable=W0603,C0103
    if event in subscribers:
        return subscribers[event]
    return []

def subscribe_to_event(event, function):
    global subscribers # pylint: disable=W0603,C0103
    if not get_all_event_functions(event):
        subscribers[event] = []
    subscribers[event].append(function)

def unsubscribe_from_event(event, function):
    global subscribers # pylint: disable=W0603,C0103
    for existing_event, _ in subscribers.items():
        if event == existing_event:
            subscribers[event].remove(function)

def init_subscriptions(list_of_modules):
    disabled_subscribers = environment.get_env_list(environment.DISABLED_SUBSCRIBERS)
    for module in list_of_modules:
        if hasattr(module, 'subscribe') and not module.__name__ in disabled_subscribers:
            module.subscribe()
