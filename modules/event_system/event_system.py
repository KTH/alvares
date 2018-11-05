__author__ = 'tinglev@kth.se'

from modules import environment

subscribers = {} # pylint: disable=C0103

def publish_event(event, data):
    global subscribers # pylint: disable=W0603,C0103
    for existing_event, function_list in subscribers.items():
        if existing_event == event:
            for function in function_list:
                function(data)

def subscribe_to_event(event, function):
    global subscribers # pylint: disable=W0603,C0103
    for existing_event, _ in subscribers.items():
        if existing_event == event:
            break
    else:
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
