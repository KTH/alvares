__author__ = 'tinglev'

import unittest
from test import mock_data
from modules import deployment_util
from modules import deployment_enricher

class DeploymentUtilTest(unittest.TestCase):

    def test_get_monitor_url_from_samples(self):
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            self.assertEqual(mock_data.expected_value(sample, 'monitorUrl'), deployment_util.get_monitor_url(sample))

    def test_get_monitor_pattern(self):
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            self.assertEqual(mock_data.expected_value(sample, 'monitorPattern'), deployment_util.get_monitor_pattern(sample))

    def test_get_application_url_from_samples(self):
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            self.assertEqual(mock_data.expected_value(sample, 'applicationUrl'), deployment_util.get_application_url(sample))

    def test_get_friendly_name_from_samples(self):
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            self.assertEqual(mock_data.expected_value(sample, 'friendlyName'), deployment_util.get_friendly_name(sample))

    def test_get_importance_from_samples(self):
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            self.assertEqual(mock_data.expected_value(sample, 'importance'), deployment_util.get_importance(sample))

    def test_get_team_from_samples(self):
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            self.assertEqual(mock_data.expected_value(sample, 'team'), deployment_util.get_team(sample))
    
    def test_get_slack_channels(self):
        for sample in mock_data.get_recommendation_samples():
            for channel in deployment_util.get_slack_channels(sample):
                self.assertEqual(
                    len(mock_data.expected_value(sample, 'slackChannels')),
                    len(deployment_util.get_slack_channels(sample)))