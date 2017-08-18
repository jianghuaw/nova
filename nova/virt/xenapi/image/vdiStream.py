# Copyright 2016 Citrix Systems
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

""" This class will handle image data in a streaming way.
"""


from os_xenapi.client import exception as xenapi_exception
from os_xenapi.client.image import vdi_handler
from oslo_log import log as logging

import nova.conf
from nova import exception
from nova import image
from nova.virt.xenapi.image.glanceStore import glanceStore
from nova.virt.xenapi.image import utils

CONF = nova.conf.CONF
LOG = logging.getLogger(__name__)

IMAGE_API = image.API()


class vdiStream(glanceStore):
    def download_image(self, context, session, instance, image_id):
        LOG.debug("in vdiStream.download_image")
        try:
            host_url = CONF.xenserver.connection_url
            image_data = IMAGE_API.download(context, image_id)
            image_stream = utils.IterableToFileAdapter(image_data)
            vdis = vdi_handler.stream_to_vdis(context, session,
                                              instance, host_url,
                                              data=image_stream)
        except xenapi_exception.OsXenApiException:
            raise exception.CouldNotFetchImage(image_id=image_id)
        return vdis

    def upload_image(self, context, session, instance, image_id, vdi_uuids):
        try:
            host_url = CONF.xenserver.connection_url
            metadata = IMAGE_API.get(context, image_id)
            metadata['disk_format'] = 'vhd'
            metadata['container_format'] = "ovf"
            # set size as zero, so that it will update the size in end basing
            # on the uploaded data.
            metadata['size'] = 0
            image_trunks = vdi_handler.vdis_to_stream(context, session,
                                                      instance, host_url,
                                                      vdi_uuids)
            image_stream = utils.IterableToFileAdapter(image_trunks)
            IMAGE_API.update(context, image_id, metadata,
                             data=image_stream)
        except xenapi_exception.OsXenApiException:
            raise exception.CouldNotUploadImage(image_id=image_id)
