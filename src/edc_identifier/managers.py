from django.db import models


class IdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class TrackingIdentifierManager(models.Manager):

    def get_by_natural_key(self, tracking_identifier):
        return self.get(tracking_identifier=tracking_identifier)
