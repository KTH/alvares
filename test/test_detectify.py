__author__ = 'tinglev'

import unittest
import os
from test import mock_data
from mock import patch
import responses
from requests import HTTPError
from modules import environment
from modules.subscribers.detectify import detectify

class DetectifyTests(unittest.TestCase):

    def test_get_api_keys(self):
        os.environ[environment.DETECTIFY_API_KEYS] = 'abc,123'
        keys = environment.get_env_list(environment.DETECTIFY_API_KEYS)
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0], 'abc')
        self.assertEqual(keys[1], '123')

    def test_should_use_cluster(self):
        os.environ[environment.DETECTIFY_CLUSTERS] = ''
        deployment = mock_data.get_deployment()
        result = detectify.should_use_cluster(deployment)
        self.assertFalse(result)
        os.environ[environment.DETECTIFY_CLUSTERS] = 'active'
        result = result = detectify.should_use_cluster(deployment)
        self.assertTrue(result)

    def test_token_list_from_json(self):
        json = [
            {
                "name": "Test",
                "endpoint": "www.test.com",
                "status": "verified",
                "created": "2018-01-10T08:34:15Z",
                "token": "abc123"
            },
            {
                "name": "Test2",
                "endpoint": "www.test2.com",
                "status": "verified",
                "created": "2018-01-10T08:34:15Z",
                "token": "abc1234"
            }
        ]
        self.assertEqual(detectify.get_token_list_from_json(json), ['abc123', 'abc1234'])

    @responses.activate
    def test_get_scan_state(self):
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/scans/abc1231/',
                      json={
                          "scan_profile_token": "5605b488634efe810dff4276e28ca7f9",
                          "created": "2018-01-10T08:34:15Z",
                          "started": "2018-01-16T16:01:38Z",
                          "phase": "general",
                          "state": "starting"}, status=200)
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/scans/abc1232/',
                      json={}, status=401)
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/scans/abc1233/',
                      body="Error 404", status=404)
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/scans/abc1234/',
                      body=HTTPError())
        state = detectify.get_scan_state('', 'abc1231')
        self.assertEqual(state, 'starting')
        self.assertRaises(detectify.DetectifyError, detectify.get_scan_state, '', 'abc1232')
        self.assertRaises(detectify.DetectifyError, detectify.get_scan_state, '', 'abc1233')
        self.assertRaises(detectify.DetectifyError, detectify.get_scan_state, '', 'abc1234')

    @responses.activate
    def test_process_api_key(self):
        api_key = 'xyz'
        deployment = mock_data.get_deployment()
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/profiles/',
                      json=[
                          {
                              "name": "Test",
                              "endpoint": "www.test.com",
                              "status": "verified",
                              "created": "2018-01-10T08:34:15Z",
                              "token": "abc123"
                          },
                          {
                              "name": "Test2",
                              "endpoint": "www.test2.com",
                              "status": "verified",
                              "created": "2018-01-10T08:34:15Z",
                              "token": "abc1234"
                          }
                      ], status=200)
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/profiles/',
                      json={}, status=400)
        detectify.process_api_key(api_key, deployment)
        self.assertRaises(detectify.DetectifyError, detectify.process_api_key, api_key, deployment)

    @responses.activate
    @patch.object(detectify, 'start_scan')
    def test_handle_deployment(self, mock_start_scan):
        os.environ[environment.DETECTIFY_CLUSTERS] = 'active'
        os.environ[environment.DETECTIFY_API_KEYS] = 'xyz1,xyz2'
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/scans/abc123xyz456/',
                      json={
                          "scan_profile_token": "abc123xyz456",
                          "created": "2018-01-10T08:34:15Z",
                          "started": "2018-01-16T16:01:38Z",
                          "phase": "general",
                          "state": "stopped"}, status=200)
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/profiles/',
                      json=[
                          {
                              "name": "Test",
                              "endpoint": "www.test.com",
                              "status": "verified",
                              "created": "2018-01-10T08:34:15Z",
                              "token": "abc123xyz456"
                          },
                          {
                              "name": "Test2",
                              "endpoint": "www.test2.com",
                              "status": "verified",
                              "created": "2018-01-10T08:34:15Z",
                              "token": "abc1234"
                          }
                      ], status=200)
        responses.add(responses.GET, 'https://api.detectify.com/rest/v2/profiles/',
                      json=[], status=200)
        responses.add(responses.POST, 'https://api.detectify.com/rest/v2/scans/abc123xyz456/',
                      json={}, status=200)
        deployment = mock_data.get_deployment()
        detectify.handle_deployment(deployment)
        mock_start_scan.assert_called_once()
        mock_start_scan.reset_mock()
        detectify.handle_deployment(deployment)
        mock_start_scan.assert_not_called()
