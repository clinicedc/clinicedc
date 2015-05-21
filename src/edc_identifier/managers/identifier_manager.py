from django.db import models


class IdentifierManager(models.Manager):
    def get_by_natural_key(self, identifier, device_id):
        return self.get(identifier=identifier, device_id=device_id)
