__author__ = 'tinglev'

import unittest
import os
from test import mock_data
from mock import patch
import responses
from requests import HTTPError
from modules import environment

class EnvironmentTests(unittest.TestCase):

    def test_is_true(self):
        os.environ["true_value"] = 'True'
        self.assertTrue(environment.is_true(os.environ["true_value"]))
        os.environ["false_value"] = 'False'
        self.assertFalse(environment.is_true(os.environ["false_value"]))
        os.environ["string_value"] = 'a-value'
        self.assertTrue(environment.is_true(os.environ["string_value"], ["a-value"]))

    def test_use_debug(self):
        # False, no env set
        self.assertFalse(environment.use_debug())
        # Falses
        self.assertFalse(environment.use_debug())
        os.environ["DEBUG"] = 'No'
        self.assertFalse(environment.use_debug())
        os.environ["DEBUG"] = 'False'
        self.assertFalse(environment.use_debug())
        # Trues
        os.environ["DEBUG"] = 'True'
        self.assertTrue(environment.use_debug())
        os.environ["DEBUG"] = 'yEs'
        self.assertTrue(environment.use_debug())
        os.environ["DEBUG"] = 'DeBug'
        self.assertTrue(environment.use_debug())
        