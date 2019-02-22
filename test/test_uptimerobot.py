__author__ = 'tinglev'

import os
import unittest
from test import mock_data
from mock import Mock
from modules.subscribers.uptimerobot import uptimerobot
from modules import environment

class UptimerobotTests(unittest.TestCase):

    def test_has_application_path(self):
        deployment = mock_data.get_deployment_with_defaults()
        self.assertTrue(uptimerobot.has_application_path(deployment))
        deployment['applicationPath'] = None
        self.assertFalse(uptimerobot.has_application_path(deployment))

    def test_app_is_excluded(self):
        os.environ[environment.UTR_EXCLUDED_APPS] = 'kth-azure-app'
        deployment = mock_data.get_deployment_with_defaults()
        self.assertTrue(uptimerobot.app_is_excluded(deployment))
        os.environ[environment.UTR_EXCLUDED_APPS] = 'tamarack'
        self.assertFalse(uptimerobot.app_is_excluded(deployment))

    def test_should_monitor_cluster(self):
        os.environ[environment.UTR_CLUSTERS] = 'stage, development'
        deployment = mock_data.get_deployment_with_defaults()
        self.assertFalse(uptimerobot.should_monitor_cluster(deployment))
        os.environ[environment.UTR_CLUSTERS] = 'stage, active'
        self.assertTrue(uptimerobot.should_monitor_cluster(deployment))

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

    def test_select_alert_contact(self):
        uptimerobot.get_alert_contacts = Mock(return_value=[
            {
                "id": "321",
                "friendly_name": "#team-pipeline",
                "type": 11,
                "status": 2,
                "value": "https://hooks.slack.com/services/abc/123/xzy"
            }
        ])
