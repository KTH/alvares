__author__ = 'tinglev'

import os
import unittest
from mock import Mock
from modules import environment
from test import mock_data
from modules import deployment_util

class DeploymentUtilTest(unittest.TestCase):

    def test_get_full_monitor_url(self):
        pass
        #deployment = mock_data.get_deployment()
        #monitor_url = deployment_util.get_full_monitor_url(deployment)
        #self.assertEqual(monitor_url, 'https://app.kth.se/kth-azure-app/_monitor')
