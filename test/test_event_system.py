__author__ = 'tinglev@kth.se'

import os
import unittest
import logging
from unittest import mock
from modules.event_system import event_system
from modules.subscribers.database import cosmosdb
from modules import environment

class TestEventSystem(unittest.TestCase):

    def test_init_susbcription(self):
        cosmosdb.subscribe = mock.Mock()
        event_system.init_subscriptions([cosmosdb])
        cosmosdb.subscribe.assert_called_once()
        cosmosdb.subscribe.reset_mock()
        cosmosdb.unsubscribe()
        os.environ[environment.DISABLED_SUBSCRIBERS] = 'modules.subscribers.database.cosmosdb'
        event_system.init_subscriptions([cosmosdb])
        cosmosdb.subscribe.assert_not_called()

    def test_get_all_event_functions(self):
        event_system.subscribe_to_event('event', self.assertIsNotNone)
        functions = event_system.get_all_event_functions('event')
        self.assertEqual(len(functions), 1)
        for func in functions:
            self.assertTrue(callable(func))
        event_system.subscribe_to_event('event', self.assertIsNotNone)
        event_system.subscribe_to_event('event2', self.assertIsNotNone)
        functions = event_system.get_all_event_functions('event')
        self.assertEqual(len(functions), 2)
        for func in functions:
            self.assertTrue(callable(func))

    def test_sub_publish_unsub(self):
        event_system.subscribe_to_event('event', self.assertIsNotNone)
        event_system.subscribe_to_event('event', raises_exception_on_no_data)
        event_system.subscribe_to_event('error', raises_exception_on_call)
        with self.assertLogs(logger=event_system.__name__, level='ERROR') as cm:
            event_system.publish_event('error', {'some': 'data'})
        self.assertEqual(len(cm.records), 1)
        event_system.unsubscribe_from_event('event', self.assertIsNotNone)
        event_system.unsubscribe_from_event('event', raises_exception_on_no_data)
        event_system.unsubscribe_from_event('error', raises_exception_on_call)
        event_system.publish_event('event', None)
        event_system.publish_event('error', {})

def raises_exception_on_no_data(data):
    if not data:
        raise Exception('Shouldnt happen')

def raises_exception_on_call(data): # pylint: disable=W0613
    raise Exception('Expected')
    