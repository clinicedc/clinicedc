from django.db import models

from ..managers import TrackingIdentifierManager
from ..simple_identifier import SimpleUniqueIdentifier, SimpleTimestampIdentifier


class TrackingIdentifier(SimpleUniqueIdentifier):
    random_string_length = 2
    template = "{device_id}{timestamp}{random_string}"
    identifier_cls = SimpleTimestampIdentifier
    make_human_readable = True


class TrackingModelMixin(models.Model):

    """A model mixin to add a tracking identifier.
    """

    tracking_identifier_cls = TrackingIdentifier
    tracking_identifier_prefix = ""

    tracking_identifier = models.CharField(max_length=30, unique=True)

    objects = TrackingIdentifierManager()

    def __str__(self):
        return f"{self.tracking_identifier[-9:]}"

    def save(self, *args, **kwargs):
        if not self.tracking_identifier:
            self.tracking_identifier = self.tracking_identifier_cls(
                identifier_prefix=self.tracking_identifier_prefix,
                identifier_type=self._meta.label_lower,
            ).identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.tracking_identifier,)

    @property
    def identifier(self):
        """Returns a shortened tracking identifier.
        """
        return self.tracking_identifier[-9:]

    class Meta:
        abstract = True
