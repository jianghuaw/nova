# Copyright 2017 Citrix System
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from os_xenapi.client import exception as xenapi_except
from os_xenapi.client.image import vdi_handler

from nova import context
from nova import exception
from nova.image.api import API as image_api
from nova.tests.unit.virt.xenapi import stubs
from nova.virt.xenapi.image import utils
from nova.virt.xenapi.image import vdi_stream


class TestGlanceStore(stubs.XenAPITestBaseNoDB):
    def setUp(self):
        super(TestGlanceStore, self).setUp()
        self.store = vdi_stream.GlanceStore()

        self.flags(connection_url='test_url',
                   group='xenserver')

        self.session = mock.Mock()
        self.context = context.RequestContext(
                'user', 'project', auth_token='foobar')
        self.instance = {'uuid': 'blah',
                         'system_metadata': [],
                         'auto_disk_config': True,
                         'os_type': 'default',
                         'xenapi_use_agent': 'true'}

    @mock.patch.object(image_api, 'download',
                       return_value='fake_data')
    @mock.patch.object(utils, 'IterableToFileAdapter',
                       return_value='fake_stream')
    @mock.patch.object(vdi_handler, 'stream_to_vdis')
    def test_download_image(self, stream_to, to_file, download):
        self.store.download_image(self.context, self.session,
                                           self.instance, 'fake_image_uuid')

        download.assert_called_once_with(self.context, 'fake_image_uuid')
        to_file.assert_called_once_with('fake_data')
        stream_to.assert_called_once_with(self.context, self.session,
                                          self.instance, 'test_url',
                                          data='fake_stream')

    @mock.patch.object(image_api, 'download',
                       return_value='fake_data')
    @mock.patch.object(utils, 'IterableToFileAdapter',
                       return_value='fake_stream')
    @mock.patch.object(vdi_handler, 'stream_to_vdis',
                       side_effect=xenapi_except.OsXenApiException)
    def test_download_image_exception(self, stream_to, to_file, download):
        self.assertRaises(exception.CouldNotFetchImage,
                          self.store.download_image,
                          self.context, self.session,
                          self.instance, 'fake_image_uuid')

    @mock.patch.object(image_api, 'get')
    @mock.patch.object(vdi_handler, 'vdis_to_stream',
                       return_value='fake_data')
    @mock.patch.object(utils, 'IterableToFileAdapter',
                       return_value='fake_stream')
    @mock.patch.object(image_api, 'update')
    def test_upload_image(self, update, to_file, to_stream, get):
        fake_vdi_uuids = ['fake-vdi-uuid']
        get.return_value = {'id': 'fake-image-id'}
        metadata = {'id': 'fake-image-id',
                    'disk_format': 'vhd',
                    'container_format': 'ovf',
                    'size': 0,
                    }
        self.store.upload_image(self.context, self.session,
                                         self.instance, 'fake_image_uuid',
                                         fake_vdi_uuids)

        get.assert_called_once_with(self.context, 'fake_image_uuid')
        to_stream.assert_called_once_with(self.context, self.session,
                                          self.instance, 'test_url',
                                          fake_vdi_uuids)
        to_file.assert_called_once_with('fake_data')
        update.assert_called_once_with(self.context, 'fake_image_uuid',
                                    metadata, data='fake_stream')

    @mock.patch.object(image_api, 'get')
    @mock.patch.object(vdi_handler, 'vdis_to_stream',
                       side_effect=xenapi_except.OsXenApiException)
    @mock.patch.object(utils, 'IterableToFileAdapter',
                       return_value='fake_stream')
    @mock.patch.object(image_api, 'update')
    def test_upload_image_exception(self, update, to_file, to_stream, get):
        fake_vdi_uuids = ['fake-vdi-uuid']
        get.return_value = {'id': 'fake-image-id'}
        self.assertRaises(exception.CouldNotUploadImage,
                          self.store.upload_image,
                          self.context, self.session,
                          self.instance, 'fake_image_uuid',
                          fake_vdi_uuids)
