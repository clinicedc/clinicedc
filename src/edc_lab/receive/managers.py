from django.db import models


class ReceiveManager(models.Manager):

    def get_by_natural_key(self, receive_identifier):
        return self.get(receive_identifier=receive_identifier)
