import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .device import Device

style = color_style()


class AppConfig(DjangoAppConfig):

    device_cls = Device

    def __init__(self, app_name, app_module):
        self._device_id = None
        super().__init__(app_name, app_module)

    name = 'edc_device'
    verbose_name = 'Edc Device'
    use_settings = False

    device_id = None
    device_role = None

    central_server_id = '99'
    middleman_id_list = ['95']
    node_server_id_list = ['98']
    client_hostname_list = []
    messages_written = False

    device_permissions = {}  # see repo example-survey for example

    def ready(self):

        device = Device(
            device_id=self.device_id,
            device_role=self.device_role,
            central_server_id=self.central_server_id,
            middlemen=self.middleman_id_list,
            nodes=self.node_server_id_list)
        for k, v in device.__dict__.items():
            setattr(self, k, v)

        if not self.messages_written:
            self.messages_written = True
            sys.stdout.write(f'Loading {self.verbose_name} ...\n')
            sys.stdout.write(
                f'  * device role is \'{self.device_role}\'; device ID is '
                f'\'{self.device_id}\'.\n')
            if self.device_permissions:
                sys.stdout.write(
                    '  * found device permissions for models:\n')
            for model in self.device_permissions:
                sys.stdout.write(f'    - {model}\n')
            sys.stdout.write(f' Done loading {self.verbose_name}.\n')
