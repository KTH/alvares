__author__ = 'tinglev@kth.se'

from unittest import mock
import unittest
import root_path
from test import mock_data
from modules.subscribers.lighthouse import lighthouse

class TestSchemaValidation(unittest.TestCase):

    def test_parse_total_score(self):
        result = lighthouse.parse_total_score(f'{root_path.PROJECT_ROOT}/test/test_report.html')
        self.assertEqual(result, 3.04)

    def test_create_file_name(self):
        deployment = mock_data.get_deployment()
        lighthouse.get_current_date_time = mock.MagicMock()
        lighthouse.get_current_date_time.return_value = '2000-01-02_13:40'
        result = lighthouse.create_file_name(deployment)
        self.assertEqual(result, 'report_kth-azure-app_active_2000-01-02_13:40.html')
