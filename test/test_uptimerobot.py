__author__ = 'tinglev'

import os
import unittest
from mock import Mock
from modules.subscribers.uptimerobot import uptimerobot
from modules import environment
from test import mock_data

class UptimerobotTests(unittest.TestCase):

    def test_get_alert_contacts(self):
        uptimerobot.call_endpoint = Mock(return_value={
            "stat": "ok",
            "offset": 0,
            "limit": 50,
            "total": 11,
            "alert_contacts": [
                {
                    "id": "123",
                    "friendly_name": "test@test.se",
                    "type": 2,
                    "status": 1,
                    "value": "test@test.se"
                },
                {
                    "id": "321",
                    "friendly_name": "#team-pipeline",
                    "type": 11,
                    "status": 2,
                    "value": "https://hooks.slack.com/services/abc/123/xzy"
                }
            ]
        })
        os.environ[environment.UTR_API_KEY] = 'abc123'
        alert_contacts = uptimerobot.get_alert_contacts()
        self.assertEqual(len(alert_contacts), 1)
        self.assertEqual(alert_contacts[0]['friendly_name'], '#team-pipeline')
