from edc_device.model_mixins import DeviceModelMixin
from edc_model_fields.fields import UUIDAutoField

from .base_model import BaseModel


class BaseUuidModel(DeviceModelMixin, BaseModel):

    """Base model class for all models using an UUID and not
    an INT for the primary key.
    """

    id = UUIDAutoField(
        blank=True,
        editable=False,
        help_text="System auto field. UUID primary key.",
        primary_key=True,
    )

    class Meta(BaseModel.Meta):
        abstract = True
