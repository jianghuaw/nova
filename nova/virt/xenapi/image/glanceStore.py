# Copyright 2017 Citrix Systems
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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class glanceStore(object):
    """Base class for glance store used to upload/download images.
    """

    @abc.abstractmethod
    def download_image(self, context, session, instance, image_id):
        """Download image from glance and create disk from image.
        """

    @abc.abstractmethod
    def upload_image(self, context, session, instance, image_id, vdi_uuids):
        """create image from disk and upload to glance.
        """
