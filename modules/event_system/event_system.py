__author__ = 'tinglev@kth.se'

subscribers = {} # pylint: disable=C0103

def publish_event(event, data):
    global subscribers # pylint: disable=W0603,C0103
    if event in subscribers:
        for function in subscribers[event]:
            function(data)

def subscribe_to_event(function, event):
    global subscribers # pylint: disable=W0603,C0103
    if not event in subscribers:
        subscribers[event] = []
    subscribers[event].append(function)

def unsubscribe_from_event(function, event):
    global subscribers # pylint: disable=W0603,C0103
    if event in subscribers:
        for sub_function in subscribers[event]:
            if sub_function == function:
                subscribers[event].remove(sub_function)
