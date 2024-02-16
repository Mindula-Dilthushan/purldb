#
# Copyright (c) nexB Inc. and others. All rights reserved.
# purldb is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/purldb for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from uuid import uuid4
import json
import os

from django.contrib.postgres.search import SearchVector
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from minecode.models import PriorityResourceURI
from minecode.models import ScannableURI
from minecode.utils_test import JsonBasedTesting
from packagedb.models import Package
from packagedb.models import PackageContentType
from packagedb.models import PackageSet
from packagedb.models import Resource
from minecode.models import ScannableURI

from unittest import mock
from univers.versions import MavenVersion

class ScannableURIAPITestCase(JsonBasedTesting, TestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'testfiles')

    def setUp(self):
        self.package1 = Package.objects.create(
            download_url='https://test-url.com/package1.tar.gz',
            type='type1',
            name='name1',
            version='1.0',
        )
        self.scannable_uri1 = ScannableURI.objects.create(
            uri='https://test-url.com/package1.tar.gz',
            package=self.package1
        )

        self.package2 = Package.objects.create(
            download_url='https://test-url.com/package2.tar.gz',
            type='type2',
            name='name2',
            version='2.0',
        )
        self.scannable_uri2 = ScannableURI.objects.create(
            uri='https://test-url.com/package2.tar.gz',
            package=self.package2
        )

        self.client = APIClient()

    def test_api_scannable_uri_list_endpoint(self):
        response = self.client.get('/api/scan_queue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, response.data.get('count'))

    def test_api_scannable_uri_get_next_download_url(self):
        response = self.client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('scannable_uri_uuid'), self.scannable_uri1.uuid)
        self.assertEqual(response.data.get('download_url'), self.scannable_uri1.uri)

        response = self.client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('scannable_uri_uuid'), self.scannable_uri2.uuid)
        self.assertEqual(response.data.get('download_url'), self.scannable_uri2.uri)

        response = self.client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('scannable_uri_uuid'), '')
        self.assertEqual(response.data.get('download_url'), '')
