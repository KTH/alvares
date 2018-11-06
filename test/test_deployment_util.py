__author__ = 'tinglev'

import os
import unittest
from mock import Mock
from modules import environment
from test import mock_data
from modules import deployment_util

class DeploymentUtilTest(unittest.TestCase):

    def test_get_full_monitor_url(self):
        deployment = mock_data.get_deployment()
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://app.kth.se/kth-azure-app/_monitor')
        deployment['applicationPath'] = '/kth-azure-app/'
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://app.kth.se/kth-azure-app/_monitor')
        deployment['monitorPath'] = 'https://absolute.path/kth-azure-app/_monitor'
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://absolute.path/kth-azure-app/_monitor')

    def test_get_full_application_url(self):
        deployment = mock_data.get_deployment()
        application_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(application_url, 'https://app.kth.se/kth-azure-app')        
        deployment['applicationPath'] = '/kth-azure-app/'
        application_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(application_url, 'https://app.kth.se/kth-azure-app')
        deployment['applicationPath'] = 'https://absolute.path/kth-azure-app/'
        application_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(application_url, 'https://absolute.path/kth-azure-app/')
