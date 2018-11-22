__author__ = 'tinglev'

import unittest
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
        deployment['cluster'] = 'stage'
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://app-r.referens.sys.kth.se/kth-azure-app/_monitor')       
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

    def test_create_friendly_name(self):
        deployment = mock_data.get_deployment()
        name = deployment_util.create_friendly_name(deployment)
        self.assertEqual(name, 'Monitor application')
        deployment['publicNameEnglish'] = None
        name = deployment_util.create_friendly_name(deployment)
        self.assertEqual(name, 'Monitorapp')
        deployment['publicNameSwedish'] = None
        name = deployment_util.create_friendly_name(deployment)
        self.assertEqual(name, 'kth-azure-app')
