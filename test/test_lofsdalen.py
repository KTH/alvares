__author__ = 'tinglev'

import unittest
from test import mock_data
from modules.subscribers.lofsdalen import lofsdalen

class LofsdalenTests(unittest.TestCase):

    def test_get_commit_hash(self):
        self.assertEqual(lofsdalen.get_commit(mock_data.get_deployment_sample_enriched()), 'abc123')

    def test_get_slack_text(self):

        mock_commited_when = {
            "commited": "2019-12-04T11:41:29Z",
            "commitedTimestamp": 1575459689,
            "nowTimestamp": 1585578602.795,
            "durationMs": 10118913.795000076,
            "readable": "4 months ago"
        }

        text = lofsdalen.get_slack_text(mock_commited_when)

        self.assertEqual('This code was pushed to :github: Github *4 months ago*.', text)