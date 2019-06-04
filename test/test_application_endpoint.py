__author__ = 'tinglev'

import os
import unittest
from test import mock_data
from mock import patch, call
from modules.subscribers.application_endpoint import application_endpoint
from modules import environment
from modules import deployment_util
from modules import deployment_enricher

class ApplicationEndpointTest(unittest.TestCase):

    def test_build_information_link(self):
        self.assertEqual(application_endpoint.build_information_link(mock_data.get_deployment_sample_enriched()), 'https://app.kth.se/pipeline/#kth-azure-app')