import copy

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase


class TestDevice(SimpleTestCase):

    def setUp(self):
        self.app_config = copy.copy(django_apps.get_app_config('edc_device'))
        self.app_config.device_id = '11'
        self.app_config.device_id = '15'
        self.server_id_list = ['99']

    def test_device_as_server(self):
        self.app_config.device_id = '99'
        self.assertTrue(self.app_config.is_central_server)

    def test_device_not_server(self):
        self.app_config.device_id = '18'
        self.assertFalse(self.app_config.is_central_server)
        self.assertTrue(self.app_config.is_client)
        self.assertEqual(self.app_config.role, 'Client')

    def test_device_returns_correct_id(self):
        self.app_config.device_id = '09'
        self.app_config.server_id_list = ['09', '99']
        self.assertTrue(self.app_config.is_server)

    def test_device_returns_correct_id3(self):
        self.app_config.device_id = '09'
        self.app_config.server_id_list = [9, '99']
        self.app_config.ready()
        self.assertFalse(self.app_config.is_server)

    def test_device_returns_correct_id2(self):
        self.app_config.device_id = 1
        self.app_config.ready()
        self.assertEqual(self.app_config.device_id, '1')

    def test_device_is_middleman(self):
        self.app_config.device_id = '96'
        self.app_config.middleman_id_list = [95, 96]
        self.app_config.ready()
        self.assertEqual(self.app_config.device_id, '96')
        self.assertEqual(self.app_config.middleman_id_list, ['95', '96'])
        self.assertFalse(self.app_config.is_central_server)
        self.assertFalse(self.app_config.is_client)
        self.assertTrue(self.app_config.is_middleman)
        self.assertEqual(self.app_config.role, 'Middleman')

    def test_device_is_node_server(self):
        self.app_config.device_id = '96'
        self.app_config.central_server = ['99']
        self.app_config.server_id_list = ['99', '96']
        self.app_config.ready()
        self.assertFalse(self.app_config.is_central_server)
        self.assertFalse(self.app_config.is_middleman)
        self.assertFalse(self.app_config.is_client)
        self.assertTrue(self.app_config.is_node_server)
        self.assertEqual(self.app_config.role, 'NodeServer')

    def test_device_with_overlapping_lists_raises(self):
        self.app_config.device_id = '96'
        self.app_config.central_server = ['99']
        self.app_config.server_id_list = [95, 96]
        self.app_config.middleman_id_list = [96]
        self.assertRaises(ImproperlyConfigured, self.app_config.ready)

#     def test_device_with_central_not_a_server_raises(self):
#         self.app_config.device_id = '96'
#         self.app_config.central_server = ['99']
#         self.app_config.server_id_list = [80, 81]
#         self.assertRaises(ImproperlyConfigured, self.app_config.ready)

    def test_central_server_is_server(self):
        self.app_config.device_id = '99'
        self.app_config.central_server_id = '99'
        self.app_config.server_id_list = [97, 96]
        self.app_config.ready()
        self.assertTrue(self.app_config.is_central_server)
        self.assertEqual(self.app_config.role, 'CentralServer')

    def test_server_is_server(self):
        self.app_config.device_id = '96'
        self.app_config.server_id_list = [95, 96, 99]
        self.app_config.middleman_id_list = [93, 94]
        self.app_config.ready()
        self.assertTrue(self.app_config.is_server)
        self.assertEqual(self.app_config.role, 'NodeServer')

    def test_middleman_is_not_server(self):
        self.app_config.device_id = '93'
        self.app_config.server_id_list = [95, 96, 99]
        self.app_config.middleman_id_list = [93, 94]
        self.app_config.ready()
        self.assertFalse(self.app_config.is_server)
        self.assertEqual(self.app_config.role, 'Middleman')
