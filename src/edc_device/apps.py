import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from . import device_permissions
from .device import Device

style = color_style()


class AppConfig(DjangoAppConfig):
    device_cls = Device

    def __init__(self, app_name, app_module):
        self._device_id = None
        super().__init__(app_name, app_module)

    name = "edc_device"
    verbose_name = "Edc Device"
    include_in_administration_section = True

    messages_written = False

    device_id = None
    device_role = None

    central_server_id = "99"
    middleman_id_list = ["95"]
    node_server_id_list = ["98"]

    def ready(self):
        from .signals import check_device_on_pre_save  # noqa

        device = Device(
            device_id=self.device_id,
            device_role=self.device_role,
            central_server_id=self.central_server_id,
            middlemen=self.middleman_id_list,
            nodes=self.node_server_id_list,
        )
        # set app_config instance attrs including device_id, device_role
        for k, v in device.__dict__.items():
            setattr(self, k, v)

        if not self.messages_written:
            self.messages_written = True
            sys.stdout.write(f"Loading {self.verbose_name} ...\n")
            sys.stdout.write(
                f"  * device id is '{self.device_id}'.\n"
                f"  * device role is '{self.device_role}'.\n"
            )
            for index, device_permission in enumerate(device_permissions):
                if index == 0:
                    sys.stdout.write("  * device permissions exist for:\n")
                sys.stdout.write(f"    - {device_permission}\n")
            sys.stdout.write(f" Done loading {self.verbose_name}.\n")
