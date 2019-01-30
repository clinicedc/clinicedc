from django.apps import apps as django_apps


class DeviceTestHelper:
    def override_device(self, device_id=None, device_role=None):
        """Overrides device ID and ROLE.

        Decorate the test method with:

            @override_settings(DEVICE_ROLE=CLIENT, DEVICE_ID='10')
            def test_blah(self):
                [...]
        """
        app_config = django_apps.get_app_config("edc_device")
        app_config.device_id = device_id
        app_config.device_role = device_role
        app_config.ready()
        assert device_id == app_config.device_id
        assert device_role == app_config.device_role
