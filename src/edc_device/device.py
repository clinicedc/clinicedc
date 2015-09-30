import re
import socket

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class DeviceClass(object):

    """ Determines the device name, useful to know when identifiers are created by the device.

    Tries settings.py (with DEVICE_ID settings attribute).
    Must be a number."""

    def __init__(self, device_id=None, central_server=None,
                 server_ids=None, middleman_ids=None):
        self.device_id = device_id or str(settings.DEVICE_ID)
        if not self.device_id:
            raise ImproperlyConfigured('Device id may not be None. See settings.DEVICE_ID')
        else:
            self.device_id = str(self.device_id)
        if not re.match(r'^\d+$', self.device_id):
            raise ImproperlyConfigured('Incorrect format for device_id. Must be a '
                                       'number. Got {1}. See settings.DEVICE_ID'.format(self.device_id))
        self.device = self.device_id
        self.central_server_id = central_server or '99'
        self.server_ids = server_ids or settings.SERVER_DEVICE_ID_LIST
        self.server_ids = [str(device_id) for device_id in self.server_ids]
        self.middleman_ids = middleman_ids or settings.MIDDLEMAN_DEVICE_ID_LIST
        self.middleman_ids = [str(device_id) for device_id in self.middleman_ids]
        self.is_server = self.device_is_server(self.device_id)
        self.is_community_server = self.device_is_community_server(self.device_id)
        self.is_central_server = self.device_is_central_server(self.device_id)
        self.is_middleman = self.device_is_middleman(self.device)
        self.role = self.device_role(self.device_id)

    def __repr__(self):
        return '<{}: {}@{}>'.format(self.role, self.device, socket.gethostname())

    def __str__(self):
        return '{}'.format(self.device)

    def device_role(self, device_id):
        if self.device_is_central_server(device_id):
            return 'CentralServer'
        elif self.device_is_community_server(device_id):
            return 'CommunityServer'
        elif self.device_is_middleman(device_id):
            return 'Middleman'
        elif self.device_is_server(device_id):
            return 'Server'
        elif self.device_is_client(device_id):
            return 'Client'
        else:
            raise ImproperlyConfigured('Unable to configure Device. See DeviceClass.')

    def device_is_client(self, device_id):
        if (not self.device_is_central_server(device_id) and
                not self.device_is_community_server(device_id) and
                not self.device_is_middleman(device_id) and
                not self.device_is_server(device_id)):
            return True
        else:
            return False

    def device_is_server(self, device_id):
        """Returns True if the device_id matches a server id"""
        return device_id in self.server_ids

    def device_is_central_server(self, device_id):
        """Returns True if the device_id matches the central server id"""
        return device_id == self.central_server_id

    def device_is_community_server(self, device_id):
        """Returns True if the device_id matches a community server id"""
        return device_id in self.server_ids and not device_id == self.central_server_id

    def device_is_middleman(self, device_id):
        """Returns True if the device_id matches a middelman id"""
        return device_id in self.middleman_ids

device = DeviceClass()
