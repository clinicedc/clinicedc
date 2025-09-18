from django.db import models
from django.utils.translation import gettext_lazy as _

from edc_model.models import BaseUuidModel


class Notification(BaseUuidModel):
    """A model that stores the notification types.

    Currently, show these for the user to select/subscribe to
    in a M2M in the edc_auth.UserProfile.

    For example:
        - a new model has been created
        - a death has occured
        - a grade 4 event has occured.
    """

    name = models.CharField(max_length=255, unique=True)

    display_name = models.CharField(max_length=255, unique=True)

    mailing_list_address = models.EmailField(_("Mailing list address"), blank=True, default="")

    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.display_name}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
