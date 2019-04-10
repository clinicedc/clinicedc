from django.test import TestCase, tag
from django.test.utils import override_settings

from ..constants import CENTRAL_SERVER, CLIENT, NODE_SERVER, MIDDLEMAN
from ..device import Device, DeviceIdError, DeviceRoleError


class TestDevice(TestCase):
    def test_device_central_server_or_defaults_to_central(self):
        """Asserts all permutations between settings and app_config
        assuming default is central.
        """
        opts_settings = [
            ("99", CENTRAL_SERVER),
            ("99", None),
            (None, CENTRAL_SERVER),
            (None, None),
        ]
        opts_config = [
            ("99", CENTRAL_SERVER),
            ("99", None),
            (None, CENTRAL_SERVER),
            (None, None),
        ]
        for DEVICE_ID, DEVICE_ROLE in opts_settings:
            with self.subTest(DEVICE_ID=DEVICE_ID, DEVICE_ROLE=DEVICE_ROLE):
                with override_settings(DEVICE_ID=DEVICE_ID, DEVICE_ROLE=DEVICE_ROLE):
                    for device_id, device_role in opts_config:
                        with self.subTest(device_id=device_id, device_role=device_role):
                            device = Device(
                                device_id=device_id, device_role=device_role
                            )
                            self.assertTrue(device.device_role == CENTRAL_SERVER)
                            self.assertTrue(device.is_central_server)

    def test_device_from_settings_only(self):
        with override_settings(DEVICE_ID="10", DEVICE_ROLE=CLIENT):
            device = Device()
        self.assertEqual(device.device_id, "10")
        self.assertEqual(device.device_role, CLIENT)

    def test_device_central_server_from_settings_raises(self):
        with override_settings(DEVICE_ID="98"):
            with self.assertRaises(DeviceIdError) as cm:
                Device(device_id="99", central_server_id="99")
            self.assertEqual(cm.exception.code, "device_id_conflict")

    def test_device_central_server_from_settings_only(self):
        with override_settings(DEVICE_ID="98"):
            device = Device(device_id=None, central_server="99", nodes=["98"])
        self.assertEqual(device.device_id, "98")
        self.assertTrue(device.is_node_server)

    def test_device_client(self):
        device = Device(device_id="33", central_server_id="99")
        self.assertTrue(device.device_role == CLIENT)
        self.assertTrue(device.is_client)
        self.assertFalse(device.is_server)
        self.assertFalse(device.is_central_server)
        self.assertFalse(device.is_node_server)
        self.assertFalse(device.is_middleman_server)

    def test_device_node_server_includes_central_raises(self):
        self.assertRaises(
            DeviceIdError,
            Device,
            device_id="98",
            central_server_id="99",
            nodes=["98", "99"],
        )

    def test_device_node_server(self):
        device = Device(device_id="98", central_server_id="99", nodes=["98"])
        self.assertTrue(device.device_role == NODE_SERVER)
        self.assertTrue(device.is_node_server)

    def test_device_middleman_includes_central_raises(self):
        self.assertRaises(
            DeviceIdError,
            Device,
            device_id="95",
            central_server_id="99",
            nodes=["98", "99"],
            middlemen=["95"],
        )

    def test_device_middleman_includes_central_raises2(self):
        self.assertRaises(
            DeviceIdError,
            Device,
            device_id="95",
            central_server_id="99",
            nodes=["98"],
            middlemen=["95", "99"],
        )

    def test_device_middleman(self):
        device = Device(
            device_id="95", central_server_id="99", nodes=["98"], middlemen=["95"]
        )
        self.assertTrue(device.device_role == MIDDLEMAN)
        self.assertTrue(device.is_middleman_server)

    def test_device_client2(self):
        device = Device(
            device_id="10", central_server_id="99", nodes=["98"], middlemen=["95"]
        )
        self.assertTrue(device.device_role == CLIENT)
        self.assertTrue(device.is_client)

    def test_device_roles_conflict(self):
        with override_settings(DEVICE_ID="98", DEVICE_ROLE=CLIENT):
            self.assertRaises(DeviceRoleError, Device, device_id="98", nodes=["98"])
