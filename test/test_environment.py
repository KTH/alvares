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
        # False, no env/value passed
        self.assertFalse(environment.is_true(None))

        # False, value passed but no values to compre against.
        self.assertFalse(environment.is_true("some-value", None))

        os.environ["env_key"] = 'True'
        self.assertTrue(environment.is_true(os.environ["env_key"]))

        os.environ["env_key"] = 'a-value'
        self.assertFalse(environment.is_true(os.environ["env_key"]))
        self.assertTrue(environment.is_true(os.environ["env_key"], ["a-value"]))
        
        os.environ["env_key"] = 'False'
        self.assertFalse(environment.is_true(os.environ["env_key"]))

        # Allow bools as ok values
        self.assertTrue(environment.is_true(True))
        self.assertFalse(environment.is_true(False))


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
        