from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Device(object):

    """ Determines the edc_device name, useful to know when identifiers are created by the edc_device.

    Tries settings.py (with DEVICE_ID settings attribute).
    Must be a number."""

    SERVER_ID = '99'
    SERVER_DEVICE_ID_LIST = settings.SERVER_DEVICE_ID_LIST
    MIDDLEMAN_DEVICE_ID_LIST = settings.MIDDLEMAN_DEVICE_ID_LIST
    DEFAULT_DEVICE_ID = '99'

    def __init__(self, device_id=None, settings_device=None):
        try:
            self.device_id = str(int(device_id))
        except (ValueError, TypeError):
            try:
                self.device_id = str(int(settings_device or settings.DEVICE_ID or self.DEFAULT_DEVICE_ID))
            except (ValueError, TypeError):
                raise ImproperlyConfigured('Invalid DEVICE_ID. Must be a number. Got {}.'.format(device_id))
            except AttributeError:
                raise ImproperlyConfigured('Missing settings attribute DEVICE_ID.')
        if len(self.device_id) != 2:
            raise ImproperlyConfigured('Invalid DEVICE_ID. Must be a two digit number. Got {}.'.format(device_id))

    def __str__(self):
        return self.device_id

    @property
    def is_server(self):
        """Returns True if the device_id is is in settings.SERVER_DEVICE_ID_LIST."""
        return self.device_id in map(str, map(int, self.SERVER_DEVICE_ID_LIST))

    @property
    def is_central_server(self):
        return self.device_id == self.SERVER_ID

    @property
    def is_community_server(self):
        return (self.device_id in map(str, map(int, self.SERVER_DEVICE_ID_LIST)) and
                not self.device_id == self.SERVER_ID)

    @property
    def is_middleman(self):
        """Returns True if the device_id is is in settings.MIDDLEMAN_DEVICE_ID_LIST."""
        if self.MIDDLEMAN_DEVICE_ID_LIST:
            return self.device_id in map(str, map(int, self.MIDDLEMAN_DEVICE_ID_LIST))

    def is_producer_name_server(self, producer_name):
        """??"""
        hostname = producer_name.split('-')[0]
        return (hostname.startswith(settings.PRODUCER_PREFIX) and
                int(hostname[4:]) in self.SERVER_DEVICE_ID_LIST)
