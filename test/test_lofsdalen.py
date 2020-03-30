__author__ = 'tinglev'

import os
import unittest
from test import mock_data
from mock import Mock
from modules.subscribers.lofsdalen import lofsdalen
from modules import environment

class LofsdalenTests(unittest.TestCase):

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