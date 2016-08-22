import re
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_device'
    verbose_name = 'Edc Device'

    device_id = '00'

    central_server_id = '99'
    node_server_id_list = None   # calculated, see below
    default_middleman_id_list = ['95']  # this needs to be removed
    default_server_id_list = ['99', '98']
    middleman_id_list = None  # if not set, uses default_middleman_id_list
    role = None  # calculated, see below
    server_id_list = None  # if not set, uses default_server_id_list

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        self.server_id_list = self.server_id_list or self.default_server_id_list
        if self.central_server_id:
            if self.central_server_id not in self.server_id_list:
                sys.stdout.write(style.NOTICE(
                    'Warning: Adding Central Server ID to list of Server IDs. See app_config.\n'))
                self.server_id_list.append(self.central_server_id)
        self.middleman_id_list = self.middleman_id_list or self.default_middleman_id_list
        if int(self.device_id) == 0:
            sys.stdout.write(style.NOTICE('Warning: Device not set, using default. See app_config.device_id\n'))
        self.device_id = str(self.device_id)
        if not re.match(r'^\d+$', self.device_id):
            raise ImproperlyConfigured('Incorrect format for device_id. Must be a '
                                       'number. Got {}. See app_config.device_id'.format(self.device_id))
        self.server_id_list = [str(x) for x in (self.server_id_list or self.default_server_id_list)]
        self.middleman_id_list = [str(x) for x in (self.middleman_id_list or self.default_middleman_id_list)]
        if list(set(self.server_id_list).intersection(self.middleman_id_list)):
            raise ImproperlyConfigured(
                'Middleman IDs cannot overlap with Server IDs. Got {}, {} respectively. '
                'See app_config'.format(self.middleman_id_list, self.server_id_list))
        self.community_server_id_list = [x for x in self.server_id_list if x != self.central_server_id]
        sys.stdout.write('  * Device ID: {}. Role: {}\n'.format(self.device_id, self.role))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def role(self):
        if self.is_central_server:
            return 'CentralServer'
        elif self.is_node_server:
            return 'NodeServer'  # a.k.a Community Server
        elif self.is_middleman:
            return 'Middleman'
        elif self.is_server:
            return 'Server'
        elif self.is_client:
            return 'Client'
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
        return self.device_id in self.community_server_id_list

    @property
    def is_middleman(self):
        """Returns True if the device_id matches a middelman id"""
        if [x for x in self.middleman_id_list if x in self.server_id_list]:
            raise ValueError('A Middleman cannot be listed as a server. {} are middlemen of '
                             'which at least one is also listed as a server.'.format(
                                 ', '.join(self.middleman_id_list)))
        return self.device_id in self.middleman_id_list
