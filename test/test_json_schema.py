__author__ = 'tinglev@kth.se'

import unittest
from test import mock_data
import requests
from modules import environment
from modules import deployment_util
from modules import deployment_enricher


class TestSchemaValidation(unittest.TestCase):

    @unittest.skipIf(environment.get_env(environment.SKIP_VALIDATION_TESTS),
                     'SKIP_VALIDATION_TESTS set')
    def test_validate_deployment_samples(self):
        furano_url = environment.get_env_with_default_value(environment.VALIDATE_DEPLOYMENT_URL, 'https://app.kth.se/jsonschema/dizin/deployment')
        for sample in mock_data.get_deployment_samples():
            del sample["mock-expected"]
            result = requests.post(furano_url, json=sample, allow_redirects=False)
            self.assertEqual(result.json(), {})
            self.assertEqual(result.status_code, 200)

    @unittest.skipIf(environment.get_env(environment.SKIP_VALIDATION_TESTS),
                     'SKIP_VALIDATION_TESTS set')
    def test_validate_deployment_samples_enriched(self):
        furano_url = environment.get_env_with_default_value(environment.VALIDATE_DEPLOYMENT_URL, 'https://app.kth.se/jsonschema/alvares/deployment')
        for sample in mock_data.get_deployment_samples():
            sample = deployment_enricher.enrich(sample)
            del sample["mock-expected"]
            result = requests.post(furano_url, json=sample, allow_redirects=False)
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

    @unittest.skipIf(environment.get_env(environment.SKIP_VALIDATION_TESTS),
                     'SKIP_VALIDATION_TESTS set')
    def test_validate_recommendation(self):
        validation_url = environment.get_env_with_default_value(
            environment.VALIDATE_DEPLOYMENT_URL,
            'https://app.kth.se/jsonschema/dizin/recommendation'
        )
        for sample in mock_data.get_recommendation_samples():
            del sample["mock-expected"]
            result = requests.post(validation_url, json=sample, allow_redirects=False)
            self.assertEqual(result.json(), {})
            self.assertEqual(result.status_code, 200)

