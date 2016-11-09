import re
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

from .constants import CENTRAL_SERVER, NODE_SERVER, MIDDLEMAN, SERVER, CLIENT

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_device'
    verbose_name = 'Edc Device'
    use_settings = False

    device_id = '00'
    central_server_id = '99'
    middleman_id_list = ['95']
    server_id_list = ['99', '98']

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        self.device_id = self.get_nonlist_attr('device_id')
        self.central_server_id = self.get_nonlist_attr('central_server_id')
        self.middleman_id_list = self.get_list_attr('middleman_id_list')
        self.server_id_list = self.get_list_attr('server_id_list')

        if not re.match(r'^\d+$', self.device_id):
            raise ImproperlyConfigured('Incorrect format for device_id. Must be a '
                                       'number. Got {}. See app_config.device_id'.format(self.device_id))
        if int(self.device_id) == 0:
            sys.stdout.write(style.NOTICE(
                '  ! Warning: Device not set, using default of \'00\'. See app_config.device_id\n'))

        if self.central_server_id not in self.server_id_list:
            ImproperlyConfigured('Central server is not listed as a server. Got {}\n'.format(self.central_server_id))

        if [x for x in self.server_id_list if x in self.middleman_id_list]:
            raise ImproperlyConfigured(
                'Middleman cannot be listed as a server. Got {} cannot be in {}. '
                'See app_config'.format(self.middleman_id_list, self.server_id_list))
        sys.stdout.write('  * device is a {} with ID {}\n'.format(self.role.lower(), self.device_id))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def _getattr(self, attrname):
        try:
            value = getattr(settings, attrname.upper())
            if not self.use_settings:
                sys.stdout.write(style.NOTICE(
                    '  ! Warning: Reading {verbose_name} from settings.{settings_attr}. \n'
                    '  !   Set AppConfig.use_settings = True to suppress this warning or \n'
                    '  !   remove attribute {settings_attr} from settings.\n').format(
                        verbose_name=' '.join(attrname.lower().split('_')),
                        settings_attr=attrname.upper()))
        except AttributeError:
            value = getattr(self, attrname.lower())
        return value

    def get_nonlist_attr(self, attrname):
        value = self._getattr(attrname)
        return value if value is None else str(value)

    def get_list_attr(self, attrname):
        value = self._getattr(attrname)
        return [str(x) for x in value if x is not None]

    @property
    def role(self):
        if self.is_central_server:
            return CENTRAL_SERVER
        elif self.is_node_server:
            return NODE_SERVER  # a.k.a Community Server
        elif self.is_middleman:
            return MIDDLEMAN
        elif self.is_server:
            return SERVER
        elif self.is_client:
            return CLIENT
        else:
            raise ImproperlyConfigured('Unable to configure Device. See DeviceClass.')

    @property
    def is_client(self):
        if (not self.is_central_server and
                not self.is_node_server and
                not self.is_middleman and
                not self.is_server):
            return True
        else:
            return False

    @property
    def is_server(self):
        """Returns True if the device_id matches a server id"""
        return self.device_id in self.server_id_list

    @property
    def is_central_server(self):
        """Returns True if the device_id matches the central server id"""
        if self.central_server_id not in self.server_id_list:
            raise ValueError('Central server must be included in the list of servers. '
                             'Got {} not in {}. See also app_config.server_id_list.'.format(
                                 self.central_server_id, self.server_id_list))
        return self.device_id == self.central_server_id

    @property
    def is_node_server(self):
        """Returns True if the device_id matches a community server id"""
        return self.device_id in [x for x in self.server_id_list if x != self.central_server_id]

    @property
    def is_middleman(self):
        """Returns True if the device_id matches a middelman id"""
        if [x for x in self.middleman_id_list if x in self.server_id_list]:
            raise ValueError('A Middleman cannot be listed as a server. Got {}.'.format(
                ', '.join(self.middleman_id_list)))
        return self.device_id in self.middleman_id_list
