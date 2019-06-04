__author__ = 'tinglev'

import os
import unittest
from test import mock_data
from mock import patch, call
from modules.subscribers.flottsbro import flottsbro
from modules import environment

class FlottsbroTests(unittest.TestCase):

    def clean(self):
        if environment.FLOTTSBRO_API_BASE_URL in os.environ:
            del os.environ[environment.FLOTTSBRO_API_BASE_URL]
        if environment.FLOTTSBRO_API_KEY in os.environ:
            del os.environ[environment.FLOTTSBRO_API_KEY]

    def test_default_base_url(self):
        self.assertEqual(flottsbro.DEFAULT_FLOTTSBRO_API_BASE_URL, flottsbro.get_base_url())

    def test_env_base_url(self):
        expected = 'https://example.com/api/path'
        os.environ[environment.FLOTTSBRO_API_BASE_URL] = expected
        self.assertEqual(flottsbro.get_base_url(), expected)
        self.clean()

    def test_get_endpoint(self):
        expected = 'https://example.com/path/v1/latest/my-cluster'
        os.environ[environment.FLOTTSBRO_API_BASE_URL] = 'https://example.com/path'
        self.assertEqual(flottsbro.get_add_endpoint('my-cluster'), expected)
        self.clean()

    def test_get_none_headers(self):
        self.assertIsNone(flottsbro.get_headers())

    def test_get_headers_with_api_key(self):
        os.environ[environment.FLOTTSBRO_API_KEY] = 's3cret-key-value'
        self.assertIsNotNone(flottsbro.get_headers())
        self.clean()

    def test_call_endpoint_without_api_key(self):
        flottsbro.call_endpoint(flottsbro.get_add_endpoint('my-cluster'), mock_data.get_deployment_sample_enriched())