__author__ = 'tinglev@kth.se'

import unittest
import root_path
from modules.subscribers.lighthouse import lighthouse

class TestSchemaValidation(unittest.TestCase):

    def test_parse_total_score(self):
        result = lighthouse.parse_total_score(f'{root_path.PROJECT_ROOT}/test/test_report.html')
        self.assertEqual(result, 3.58)
