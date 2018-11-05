__author__ = 'tinglev'

import os
import unittest
from mock import patch, call
from modules.subscribers.slack import slack_util, slack_deployment, slack_error
from modules import environment
from test import mock_data

class SlackTests(unittest.TestCase):

    def test_add_attachment_to_body(self):
        body = {'attr': 'value', 'attr2': 'value2'}
        attachment = {'a': 'b', 'c': 'd'}
        body = slack_util.add_attachment_to_body(body, attachment)
        self.assertEqual(body, {'attr': 'value', 'attr2': 'value2',
                                'attachments': [{'a': 'b', 'c': 'd'}]})
        body = slack_util.add_attachment_to_body(body, attachment)
        self.assertEqual(body, {'attr': 'value', 'attr2': 'value2',
                                'attachments': [{'a': 'b', 'c': 'd'},
                                                {'a': 'b', 'c': 'd'}]})

    # def test_get_attachment(self):
    #     slack_middleware = Slack('slack')
    #     deployment = test_data.create_test_deployment()
    #     attachment = slack_middleware.get_attachment(deployment)
    #     self.maxDiff = None
    #     log_link = ('https://kth-production.portal.mms.microsoft.com/?returnUrl=%2F#Workspace/search/index?_timeInterval.intervalDuration=604800&is=false&q=search%20dockerinfo_labels_se_kth_imageName_s%3D%3D%22kth-azure-app%22%20and%20dockerinfo_labels_se_kth_imageVersion_s%3D%3D%221.3.4_abc123%22%20and%20dockerinfo_labels_se_kth_cluster_s%3D%3D%22stage%22%20%7C%20project%20time_t%2C%20msg_s%2C%20err_stack_s%20%7C%20render%20table%20%7C%20sort%20by%20time_t%20desc')

    #     assertValue = {'author_link': log_link,
    #                                   'author_name': 'View logs for this deployment',
    #                                   'color': '#36a64f',
    #                                   'fallback': 'Your client does not support attachments :(',
    #                                   'text': 'Application version: 1.3.4_abc123',
    #                                   'title': 'Application name: kth-azure-app'}
        
    #     self.assertEqual(attachment, assertValue)

    def test_create_deployment_message(self):
        deployment = mock_data.get_deployment()
        message = slack_deployment.create_deployment_message(deployment)
        self.assertEqual(message, '*kth-azure-app* deployed in *active*')

    def test_create_error_message(self):
        error = mock_data.get_error()
        message = slack_error.create_error_message(error)
        self.assertEqual(message, '*An error occured* '
                                  '```\nThis is a multiline\nstack trace\n```')

    def test_create_error_message_no_stack_trace(self):
        error = mock_data.get_error()
        error['stackTrace'] = None
        message = slack_error.create_error_message(error)
        self.assertEqual(message, 'An error occured')

    @patch.object(slack_deployment, 'send_deployment_to_slack')
    def test_handle_deployment(self, mock_send):
        deployment = mock_data.get_deployment()
        os.environ[environment.SLACK_WEB_HOOK] = 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7'
        os.environ[environment.SLACK_CHANNELS] = '#zermatt,#developers'
        slack_deployment.handle_deployment(deployment)
        calls = [
            call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', '#zermatt', deployment),
            call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', '#developers', deployment),
            call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', '#team-pipeline', deployment),
        ]
        mock_send.assert_has_calls(calls, any_order=True)
        mock_send.reset_mock()
        os.environ[environment.SLACK_CHANNEL_OVERRIDE] = '#override'
        calls = [call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', '#override', deployment)]
        slack_deployment.handle_deployment(deployment)
        mock_send.assert_has_calls(calls, any_order=True)

    @patch.object(slack_error, 'call_slack_endpoint')
    def test_handle_error_override(self, mock_send):
        error = mock_data.get_error()
        os.environ[environment.SLACK_WEB_HOOK] = 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7'
        os.environ[environment.SLACK_CHANNELS] = '#zermatt,#developers'
        os.environ[environment.SLACK_CHANNEL_OVERRIDE] = '#override'
        slack_error.handle_error(error)
        error_message = slack_error.create_error_message(error)
        payload_1 = {
            "channel": '#override',
            "text": error_message,
            "username": 'Alvares Error',
            "icon_emoji": ':no_entry:'
        }
        calls = [
            call('#override', 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_1)
        ]
        mock_send.assert_has_calls(calls, any_order=True)

    @patch.object(slack_error, 'call_slack_endpoint')
    def test_handle_error_with_channels(self, mock_send):
        error = mock_data.get_error()
        os.environ[environment.SLACK_WEB_HOOK] = 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7'
        os.environ[environment.SLACK_CHANNELS] = '#zermatt,#developers'
        del os.environ[environment.SLACK_CHANNEL_OVERRIDE]
        slack_error.handle_error(error)
        error_message = slack_error.create_error_message(error)
        payload_1 = {
            "channel": '#team-pipeline-logs',
            "text": error_message,
            "username": 'Alvares Error',
            "icon_emoji": ':no_entry:'
        }
        payload_2 = {
            "channel": '#ita-ops',
            "text": error_message,
            "username": 'Alvares Error',
            "icon_emoji": ':no_entry:'
        }
        calls = [
            call('#team-pipeline-logs', 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_1),
            call('#ita-ops', 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_2),
        ]
        mock_send.assert_has_calls(calls, any_order=True)

    @patch.object(slack_error, 'call_slack_endpoint')
    def test_handle_error_no_channels(self, mock_send):
        error = mock_data.get_error()
        os.environ[environment.SLACK_WEB_HOOK] = 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7'
        os.environ[environment.SLACK_CHANNELS] = '#zermatt,#developers'
        del os.environ[environment.SLACK_CHANNEL_OVERRIDE]
        error['slackChannels'] = None
        slack_error.handle_error(error)
        error_message = slack_error.create_error_message(error)
        payload_1 = {
            "channel": '#zermatt',
            "text": error_message,
            "username": 'Alvares Error',
            "icon_emoji": ':no_entry:'
        }
        payload_2 = {
            "channel": '#developers',
            "text": error_message,
            "username": 'Alvares Error',
            "icon_emoji": ':no_entry:'
        }
        calls = [
            call('#zermatt', 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_1),
            call('#developers', 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_2),
        ]
        mock_send.assert_has_calls(calls, any_order=True)
