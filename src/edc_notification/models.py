from django.db import models
from django.utils.translation import gettext_lazy as _
from edc_model import models as edc_models


class Notification(edc_models.BaseUuidModel):

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

    mailing_list_address = models.EmailField(
        _("Mailing list address"), blank=True, null=True
    )

    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.display_name}"

    class Meta(edc_models.BaseUuidModel.Meta):
        ordering = ("display_name",)
