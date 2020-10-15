__author__ = 'tinglev'

import os
import unittest
from test import mock_data
from mock import patch, call
from modules.subscribers.slack import slack_util, slack_deployment, slack_error
from modules import environment

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

    def test_get_attachment(self):
        deployment = mock_data.get_deployment_sample_enriched()
        attachment = slack_util.get_attachment(deployment)
        log_link = ('https://graycloud.ite.kth.se/search?rangetype=relative&'
                    'fields=message%2Csource&width=2560&highlightMessage=&'
                    'relative=3600&q=source%3Aactive+AND+image_name%3A'
                    '/.%2Akth-azure-app%3A2.0.11_abc123.%2A/')
        self.assertEqual(attachment['author_name'], ':mag: Search Logs')
        self.assertEqual(attachment['text'], 'Image version: 2.0.11_abc123')
        self.assertEqual(attachment['title'], 'Image name: kth-azure-app')
        self.assertEqual(attachment['author_link'], log_link)

    def test_create_deployment_message(self):
        deployment = mock_data.get_deployment_sample_enriched()
        message = slack_deployment.create_deployment_message(deployment)
        self.assertEqual(message, '3 replica(s) of *kth-azure-app* are being deployed in *active*, this may take up to 30 seconds.')

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
        deployment = mock_data.get_deployment_sample_enriched()
        del os.environ[environment.SLACK_CHANNEL_OVERRIDE]
        os.environ[environment.SLACK_WEB_HOOK] = ('https://hooks.slack.com/services/'
                                                  'T02KE/B4PH1/VmEd2c7')
        os.environ[environment.SLACK_CHANNELS] = '#zermatt,#developers'
        slack_deployment.handle_deployment(deployment)
        calls = [
            call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7',
                 '#zermatt', deployment),
            call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7',
                 '#developers', deployment),
            call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7',
                 '#team-studadm', deployment),
        ]
        # Print actual calls - for debugging
        #for c in mock_send.call_args_list:
        #    print(c)
        mock_send.assert_has_calls(calls, any_order=True)
        mock_send.reset_mock()
        os.environ[environment.SLACK_CHANNEL_OVERRIDE] = '#override'
        calls = [call('https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7',
                      '#override', deployment)]
        slack_deployment.handle_deployment(deployment)
        mock_send.assert_has_calls(calls, any_order=True)

    @patch.object(slack_error, 'call_slack_endpoint')
    def test_handle_error_override(self, mock_send):
        error = mock_data.get_error()
        os.environ[environment.SLACK_WEB_HOOK] = ('https://hooks.slack.com/services/'
                                                  'T02KE/B4PH1/VmEd2c7')
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
        os.environ[environment.SLACK_WEB_HOOK] = ('https://hooks.slack.com/services/'
                                                  'T02KE/B4PH1/VmEd2c7')
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
            call('#team-pipeline-logs',
                 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_1),
            call('#ita-ops',
                 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_2),
        ]
        mock_send.assert_has_calls(calls, any_order=True)

    @patch.object(slack_error, 'call_slack_endpoint')
    def test_handle_error_no_channels(self, mock_send):
        error = mock_data.get_error()
        os.environ[environment.SLACK_WEB_HOOK] = ('https://hooks.slack.com/services/'
                                                  'T02KE/B4PH1/VmEd2c7')
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
            call('#zermatt',
                 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_1),
            call('#developers',
                 'https://hooks.slack.com/services/T02KE/B4PH1/VmEd2c7', payload_2),
        ]
        mock_send.assert_has_calls(calls, any_order=True)

    def test_get_deployment_channels(self):
        deployment = mock_data.get_deployment_sample_enriched()
        channels = slack_util.get_deployment_channels(deployment)
        self.assertEqual(channels, ['#developers', '#team-studadm'])

        os.environ[environment.SLACK_CHANNELS] = '#team-ateam'
        channels = slack_util.get_deployment_channels(deployment)
        self.assertEqual(channels, ['#team-ateam', '#developers', '#team-studadm'])

        os.environ[environment.SLACK_CHANNELS] = '#team-ateam, #general'
        channels = slack_util.get_deployment_channels(deployment)

        self.assertEqual(channels, ['#team-ateam', '#general', '#developers', '#team-studadm'])
        os.environ[environment.SLACK_CHANNEL_OVERRIDE] = '#override'
        channels = slack_util.get_deployment_channels(deployment)

        self.assertEqual(channels, ['#override'])
