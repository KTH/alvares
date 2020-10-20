__author__ = 'paddy'

from modules.subscribers.uptimerobot.uptimerobot import call_endpoint
from modules import deployment_enricher
import os
import unittest
from test import mock_data
from mock import Mock, patch
from modules.subscribers.uptimerobot import uptimerobot
from modules import environment
from modules import feature_flags

class UptimerobotTests(unittest.TestCase):

    @patch.object(uptimerobot, 'select_alert_contact')
    @patch.object(uptimerobot, 'call_endpoint')
    def test_modify_or_add_monitor(self, call_endpoint, _):
        deployment = mock_data.get_deployment_sample_enriched()
        # New monitor
        uptimerobot.modify_or_add_monitor(deployment)
        call_endpoint.assert_called_once()
        call_endpoint.assert_called_with(
            '/newMonitor',
            uptimerobot.get_api_payload(deployment)
        )

        # Delete monitor
        call_endpoint.reset_mock()
        os.environ[feature_flags.FEATURE_FLAG_UTR_DELETE_ON_ZERO_REPLICAS] = 'True'
        deployment['replicas'] = '0'
        uptimerobot.modify_or_add_monitor(deployment, 1)
        call_endpoint.assert_called_once()
        call_endpoint.assert_called_with(
            '/deleteMonitor',
            uptimerobot.get_api_payload(deployment, 1)
        )
        del os.environ[feature_flags.FEATURE_FLAG_UTR_DELETE_ON_ZERO_REPLICAS]

        # Do nothing
        call_endpoint.reset_mock()
        uptimerobot.modify_or_add_monitor(deployment)
        call_endpoint.assert_not_called()

        # Edit monitor
        call_endpoint.reset_mock()
        deployment['replicas'] = 'global'
        uptimerobot.modify_or_add_monitor(deployment, 1)
        call_endpoint.assert_called_once()
        call_endpoint.assert_called_with(
            '/editMonitor',
            uptimerobot.get_api_payload(deployment, 1)
        )

    def test_has_application_path(self):
        deployment = mock_data.get_deployment_sample_enriched()
        self.assertTrue(uptimerobot.has_application_path(deployment))
        deployment['applicationPath'] = None
        self.assertFalse(uptimerobot.has_application_path(deployment))

    def test_app_is_excluded(self):
        os.environ[environment.UTR_EXCLUDED_APPS] = 'kth-azure-app'
        deployment = mock_data.get_deployment_sample_enriched()
        self.assertTrue(uptimerobot.app_is_excluded(deployment))
        os.environ[environment.UTR_EXCLUDED_APPS] = 'tamarack'
        self.assertFalse(uptimerobot.app_is_excluded(deployment))

    def test_should_monitor_cluster(self):
        os.environ[environment.UTR_CLUSTERS] = 'stage, development'
        deployment = mock_data.get_deployment_sample_enriched()
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
        studadm_id = 321
        uptimerobot.get_alert_contacts = Mock(return_value=[
            {
                "id": "123",
                "friendly_name": "#team-pipeline",
                "type": 11,
                "status": 2,
                "value": "https://hooks.slack.com/services/abc/123/xzy"
            },
            {
                "id": studadm_id,
                "friendly_name": "#team-studadm-alert",
                "type": 11,
                "status": 2,
                "value": "https://hooks.slack.com/services/abc/321/xzy"
            },
            {
                "id": "231",
                "friendly_name": "#team-kth-webb-alert",
                "type": 11,
                "status": 2,
                "value": "https://hooks.slack.com/services/abc/231/xzy"
            }
        ])

        deployment = mock_data.get_deployment_sample_enriched()

        self.assertEqual(studadm_id, uptimerobot.select_alert_contact(deployment))
