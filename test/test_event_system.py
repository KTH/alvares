__author__ = 'tinglev@kth.se'

import unittest
from modules.event_system import event_system

class TestEventSystem(unittest.TestCase):

    def test_all(self):
        event_system.subscribe_to_event('event', self.assertIsNotNone)
        event_system.subscribe_to_event('event', raises_exception_on_no_data)
        event_system.publish_event('event', {'some': 'data'})
        event_system.unsubscribe_from_event('event', self.assertIsNotNone)
        event_system.unsubscribe_from_event('event', raises_exception_on_no_data)
        event_system.publish_event('event', None)

def raises_exception_on_no_data(data):
    if not data:
        raise Exception('Shouldnt happen')
    