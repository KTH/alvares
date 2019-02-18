__author__ = 'tinglev'

import unittest
from test import mock_data
from modules import deployment_util

class DeploymentUtilTest(unittest.TestCase):

    def test_get_full_monitor_url(self):
        deployment = mock_data.get_deployment()
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://app.kth.se/kth-azure-app/_monitor')
    
    def test_get_full_monitor_url_applicationPath(self):
        deployment = mock_data.get_deployment()
        deployment['applicationPath'] = '/kth-azure-app/'

        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://app.kth.se/kth-azure-app/_monitor')

    def test_get_full_monitor_url_is_stage(self):
        deployment = mock_data.get_deployment()
        deployment['cluster'] = 'stage'
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://app-r.referens.sys.kth.se/kth-azure-app/_monitor')

    def test_get_full_monitor_url_monitorPath(self):
        deployment = mock_data.get_deployment()
        deployment['monitorPath'] = 'https://absolute.path/kth-azure-app/_monitor'
        monitor_url = deployment_util.get_full_monitor_url(deployment)
        self.assertEqual(monitor_url, 'https://absolute.path/kth-azure-app/_monitor')

    def test_get_full_monitor_url_no_monitorPath(self):
        deployment = mock_data.get_deployment()
        expected_url = 'https://app.kth.se/kth-azure-app/_monitor'
        del deployment['monitorPath']
        self.assertEqual(expected_url, deployment_util.get_full_monitor_url(deployment))


    def test_get_full_monitor_url_no_monitorPath_no_application_last_slash(self):
        deployment = mock_data.get_deployment()
        expected_url = 'https://app.kth.se/kth-azure-app/_monitor'
        del deployment['monitorPath']
        deployment['applicationPath'] = '/kth-azure-app'
        self.assertEqual(expected_url, deployment_util.get_full_monitor_url(deployment))

    def test_monitor_path_default_path(self):
        deployment = mock_data.get_deployment()
        expected_url = '/_monitor'
        self.assertEqual(expected_url, deployment_util.get_monitor_path(deployment))

    def test_monitor_path_explicit_path(self):
        deployment = mock_data.get_deployment()
        expected_url = 'https://absolute.path/kth-azure-app/_monitor'
        deployment['monitorPath'] = expected_url
        self.assertEqual(expected_url, deployment_util.get_monitor_path(deployment))

    def test_monitor_path_explicit_path_no_ending_slash(self):
        deployment = mock_data.get_deployment()
        expected_url = 'https://absolute.path/kth-azure-app/_monitor'
        del  deployment['monitorPath']
        del  deployment['applicationPath']
        deployment['applicationPath'] = '/kth-azure-app'
        deployment['monitorPath'] = expected_url
        self.assertEqual(expected_url, deployment_util.get_monitor_path(deployment))

    def test_get_full_application_url(self):
        deployment = mock_data.get_deployment()
        application_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(application_url, 'https://app.kth.se/kth-azure-app')
        deployment['applicationPath'] = '/kth-azure-app/'
        application_url = deployment_util.get_full_application_url(deployment)
        deployment['cluster'] = 'stage'
        monitor_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(monitor_url, 'https://app-r.referens.sys.kth.se/kth-azure-app')
        self.assertEqual(application_url, 'https://app.kth.se/kth-azure-app')
        deployment['applicationPath'] = 'https://absolute.path/kth-azure-app/'
        application_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(application_url, 'https://absolute.path/kth-azure-app/')
        del deployment['applicationPath']
        application_url = deployment_util.get_full_application_url(deployment)
        self.assertEqual(application_url, '')

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
