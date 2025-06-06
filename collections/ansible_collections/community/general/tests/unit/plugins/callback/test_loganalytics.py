# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.executor.task_result import TaskResult
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch, Mock
from ansible_collections.community.general.plugins.callback.loganalytics import AzureLogAnalyticsSource

from datetime import datetime
import json
import sys


class TestAzureLogAnalytics(unittest.TestCase):
    @patch('ansible_collections.community.general.plugins.callback.loganalytics.socket')
    def setUp(self, mock_socket):
        mock_socket.gethostname.return_value = 'my-host'
        mock_socket.gethostbyname.return_value = '1.2.3.4'
        self.loganalytics = AzureLogAnalyticsSource()
        self.mock_task = Mock('MockTask')
        self.mock_task._role = 'myrole'
        self.mock_task._uuid = 'myuuid'
        self.task_fields = {'args': {}}
        self.mock_host = Mock('MockHost')
        self.mock_host.name = 'myhost'

        # Add backward compatibility
        if sys.version_info < (3, 2):
            self.assertRegex = self.assertRegexpMatches

    @patch('ansible_collections.community.general.plugins.callback.loganalytics.now')
    @patch('ansible_collections.community.general.plugins.callback.loganalytics.open_url')
    def test_overall(self, open_url_mock, mock_now):
        mock_now.return_value = datetime(2020, 12, 1)
        result = TaskResult(host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields)

        self.loganalytics.send_event(workspace_id='01234567-0123-0123-0123-01234567890a',
                                     shared_key='dZD0kCbKl3ehZG6LHFMuhtE0yHiFCmetzFMc2u+roXIUQuatqU924SsAAAAPemhjbGlAemhjbGktTUJQAQIDBA==',
                                     state='OK',
                                     result=result,
                                     runtime=100)

        args, kwargs = open_url_mock.call_args
        sent_data = json.loads(args[1])

        self.assertEqual(sent_data['event']['timestamp'], 'Tue, 01 Dec 2020 00:00:00 GMT')
        self.assertEqual(sent_data['event']['host'], 'my-host')
        self.assertEqual(sent_data['event']['uuid'], 'myuuid')
        self.assertEqual(args[0], 'https://01234567-0123-0123-0123-01234567890a.ods.opinsights.azure.com/api/logs?api-version=2016-04-01')

    @patch('ansible_collections.community.general.plugins.callback.loganalytics.now')
    @patch('ansible_collections.community.general.plugins.callback.loganalytics.open_url')
    def test_auth_headers(self, open_url_mock, mock_now):
        mock_now.return_value = datetime(2020, 12, 1)
        result = TaskResult(host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields)

        self.loganalytics.send_event(workspace_id='01234567-0123-0123-0123-01234567890a',
                                     shared_key='dZD0kCbKl3ehZG6LHFMuhtE0yHiFCmetzFMc2u+roXIUQuatqU924SsAAAAPemhjbGlAemhjbGktTUJQAQIDBA==',
                                     state='OK',
                                     result=result,
                                     runtime=100)

        args, kwargs = open_url_mock.call_args
        headers = kwargs['headers']

        self.assertRegex(headers['Authorization'], r'^SharedKey 01234567-0123-0123-0123-01234567890a:.*=$')
        self.assertEqual(headers['Log-Type'], 'ansible_playbook')
