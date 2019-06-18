__author__ = 'tinglev@kth.se'

import unittest
from test import mock_data
from modules.subscribers.slack import slack_recommendation

class TestSlackRecommendation(unittest.TestCase):

    def test_slack_message_not_changed(self):
        for sample in mock_data.get_recommendation_samples():
            self.assertEqual(mock_data.expected_value(sample, 'message'), sample['message'])

    def test_slack_channels_split_works(self):
        for sample in mock_data.get_recommendation_samples():
            self.assertEqual(
                len(mock_data.expected_value(sample, 'slackChannels')),
                len(slack_recommendation.get_slack_channels(sample)))

    def test_slack_channels_is_none(self):
        recommendation = {'slackChannels': None}
        result = slack_recommendation.get_slack_channels(recommendation)
        self.assertEqual([], result)
