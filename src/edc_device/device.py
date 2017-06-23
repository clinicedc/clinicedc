from copy import copy
from django.conf import settings
from django.core.exceptions import ValidationError

from .constants import CENTRAL_SERVER, NODE_SERVER, MIDDLEMAN, CLIENT
from pprint import pprint


class DeviceIdError(ValidationError):
    pass


class DeviceRoleError(ValidationError):
    pass


class Device:

    default_central_server_id = '99'
    default_device_id = '99'
    default_role = CENTRAL_SERVER

    def __init__(self, device_id=None, device_role=None, central_server_id=None,
                 nodes=None, middlemen=None, **kwargs):

        self.central_server_id = central_server_id or self.default_central_server_id
        self.nodes = nodes or []
        self.middlemen = middlemen or []

        if central_server_id in self.nodes:
            raise DeviceIdError(
                f'Central server ID may not be included with node IDs. '
                f'Got {self.central_server_id}, nodes={self.nodes}.')
        elif central_server_id in self.middlemen:
            raise DeviceIdError(
                f'Central server ID may not be included with middleman IDs. '
                f'Got {self.central_server_id}, middlemen={self.middlemen}.')

        self.servers = copy(nodes or [])
        self.servers.append(self.central_server_id)
        self.servers.extend(self.middlemen)

        self.is_central_server = False
        self.is_node_server = False
        self.is_middleman_server = False
        self.is_client = False

        self.is_server = True

        self.device_id = self.get_device_id(device_id)
        if not self.device_id:
            self.device_id = self.default_device_id
        self.device_role = self.get_device_role(device_role)

    def get_device_role(self, device_role=None):

        if self.device_id == self.central_server_id:
            role = CENTRAL_SERVER
            self.is_central_server = True
        elif self.device_id in self.nodes:
            role = NODE_SERVER
            self.is_node_server = True
        elif self.device_id in self.middlemen:
            role = MIDDLEMAN
            self.is_middleman_server = True
        else:
            role = CLIENT
            self.is_client = True
            self.is_server = False

        try:
            assert settings.DEVICE_ROLE == role
        except AttributeError:
            pass
        except AssertionError:
            if settings.DEVICE_ROLE:
                raise DeviceRoleError(
                    f'AppConfig.device_role conflicts with settings.DEVICE_ROLE '
                    f'Got {device_role} != {settings.DEVICE_ROLE}',
                    code='device_role_conflict')

        return role

    def get_device_id(self, device_id=None):
        try:
            value = settings.DEVICE_ID
        except AttributeError:
            value = device_id
        else:
            value = value or device_id
#         if not value:
#             raise DeviceIdError(
#                 f'Unable to determine device_id. Check settings.DEVICE_ID '
#                 'and/or AppConfig.', code='device_id_none')
        if value and device_id:
            try:
                assert value == device_id
            except AssertionError:
                raise DeviceIdError(
                    f'AppConfig.device_id conflicts with settings.DEVICE_ID '
                    f'Got \'{device_id}\' != \'{settings.DEVICE_ID}\'',
                    code='device_id_conflict')
        return value
