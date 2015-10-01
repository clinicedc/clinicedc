from django.test import SimpleTestCase
from django.test.utils import override_settings

from edc_device.device import DeviceClass


class TestDevice(SimpleTestCase):

    @override_settings(DEVICE_ID='99')
    def test_device_as_server(self):
        device = DeviceClass()
        self.assertEqual(str(device), '99')
        self.assertTrue(device.is_central_server)
        device = DeviceClass(device_id='99')
        self.assertEqual(str(device), '99')
        self.assertTrue(device.is_central_server)

    @override_settings(DEVICE_ID='18')
    def test_device_not_server(self):
        device = DeviceClass()
        self.assertEqual(str(device), '18')
        self.assertFalse(device.is_central_server)
        self.assertTrue(device.is_client)
        self.assertEqual(device.role, 'Client')

    @override_settings(DEVICE_ID='09', SERVER_DEVICE_ID_LIST=['09', '99'])
    def test_device_returns_correct_id(self):
        device = DeviceClass()
        self.assertEqual(str(device), '09')
        self.assertTrue(device.is_server)

    @override_settings(DEVICE_ID='09', SERVER_DEVICE_ID_LIST=[9, '99'])
    def test_device_returns_correct_id3(self):
        device = DeviceClass()
        self.assertEqual(str(device), '09')
        self.assertFalse(device.is_server)

    @override_settings(DEVICE_ID=1)
    def test_device_returns_correct_id2(self):
        device = DeviceClass()
        self.assertEqual(str(device), '1')

    @override_settings(DEVICE_ID='96', MIDDLEMAN_DEVICE_ID_LIST=[95, 96])
    def test_device_is_middleman(self):
        device = DeviceClass()
        self.assertEqual(str(device), '96')
        self.assertFalse(device.is_central_server)
        self.assertFalse(device.is_client)
        self.assertTrue(device.is_middleman)
        self.assertEqual(device.role, 'Middleman')

    @override_settings(DEVICE_ID='96', SERVER_DEVICE_ID_LIST=[95, 96, 99], MIDDLEMAN_DEVICE_ID_LIST=[])
    def test_device_is_community_server(self):
        device = DeviceClass()
        self.assertEqual(str(device), '96')
        self.assertFalse(device.is_central_server)
        self.assertFalse(device.is_middleman)
        self.assertFalse(device.is_client)
        self.assertTrue(device.is_community_server)
        self.assertEqual(device.role, 'CommunityServer')

    @override_settings(DEVICE_ID='96', SERVER_DEVICE_ID_LIST=[95, 96], MIDDLEMAN_DEVICE_ID_LIST=[96])
    def test_device_with_overlapping_lists_raises(self):
        self.assertRaises(ValueError, DeviceClass)

    @override_settings(DEVICE_ID='96', SERVER_DEVICE_ID_LIST=[80, 81], DEFAULT_CENTRAL_SERVER_ID=99)
    def test_device_with_central_not_a_server_raises(self):
        self.assertRaises(ValueError, DeviceClass)

    @override_settings(DEVICE_ID='99', SERVER_DEVICE_ID_LIST=[95, 96, 99], MIDDLEMAN_DEVICE_ID_LIST=[93, 94])
    def test_central_server_is_server(self):
        device = DeviceClass()
        self.assertTrue(device.is_server)
        self.assertEqual(device.role, 'CentralServer')

    @override_settings(DEVICE_ID='96', SERVER_DEVICE_ID_LIST=[95, 96, 99], MIDDLEMAN_DEVICE_ID_LIST=[93, 94])
    def test_server_is_server(self):
        device = DeviceClass()
        self.assertTrue(device.is_server)
        self.assertEqual(device.role, 'CommunityServer')

    @override_settings(DEVICE_ID='93', SERVER_DEVICE_ID_LIST=[95, 96, 99], MIDDLEMAN_DEVICE_ID_LIST=[93, 94])
    def test_middleman_is_not_server(self):
        device = DeviceClass()
        self.assertFalse(device.is_server)
        self.assertEqual(device.role, 'Middleman')
