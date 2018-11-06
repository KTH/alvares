__author__ = 'tinglev@kth.se'

import unittest
import requests
from test import mock_data
from modules import environment

class TestSchemaValidation(unittest.TestCase):

    @unittest.skipIf(environment.get_env(environment.SKIP_VALIDATION_TESTS),
                     'SKIP_VALIDATION_TESTS set')
    def test_validate_deployment(self):
        validation_url = environment.get_env_with_default_value(
            environment.VALIDATE_DEPLOYMENT_URL,
            'https://app.kth.se/jsonschema/dizin/deployment'
        )
        deployment_json = mock_data.get_deployment()
        result = requests.post(validation_url, json=deployment_json, allow_redirects=False)
        self.assertEqual(result.json(), {})
        self.assertEqual(result.status_code, 200)

    @unittest.skipIf(environment.get_env(environment.SKIP_VALIDATION_TESTS),
                     'SKIP_VALIDATION_TESTS set')
    def test_validate_error(self):
        validation_url = environment.get_env_with_default_value(
            environment.VALIDATE_DEPLOYMENT_URL,
            'https://app.kth.se/jsonschema/dizin/error'
        )
        deployment_json = mock_data.get_error()
        result = requests.post(validation_url, json=deployment_json, allow_redirects=False)
        self.assertEqual(result.json(), {})
        self.assertEqual(result.status_code, 200)
