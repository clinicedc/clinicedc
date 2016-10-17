from django.db import models


class DestinationManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class PackingListManager(models.Manager):

    def get_by_natural_key(self, timestamp):
        return self.get(timestamp=timestamp)


class PackingListItemManager(models.Manager):

    def get_by_natural_key(self, item_reference):
        return self.get(item_reference=item_reference)
