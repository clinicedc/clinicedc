from django.utils.translation import gettext as _
from django.db.models import CharField


class OtherCharField(CharField):
    """Field for "Other specify" options
    """

    description = _("Custom field for 'Other specify' form field")

    DEFAULT_MAX_LENGTH = 35

    def __init__(self, *args, **kwargs):
        kwargs.update(blank=True)
        kwargs.update(null=True)
        kwargs.setdefault("max_length", self.DEFAULT_MAX_LENGTH)
        kwargs.setdefault("verbose_name", _("If other, please specify ..."))
        self.max_length = kwargs["max_length"]
        self.verbose_name = kwargs["verbose_name"]
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.update(blank=True)
        kwargs.update(null=True)
        kwargs.update(max_length=self.max_length)
        kwargs.update(verbose_name=self.verbose_name)
        return name, path, args, kwargs
