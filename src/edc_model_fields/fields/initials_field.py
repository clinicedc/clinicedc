import re

from django.db.models import CharField
from django.forms import RegexField
from django.utils.translation import gettext as _


class InitialsField(CharField):
    description = _("Custom field for a person's initials")

    def __init__(self, metadata=None, *args, **kwargs):
        self.metadata = metadata
        kwargs.setdefault("editable", True)
        kwargs.setdefault("verbose_name", _("Initials"))
        kwargs.setdefault("max_length", 3)
        kwargs.setdefault("help_text", _("Type 2-3 letters, all in uppercase and no spaces"))
        CharField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.metadata is not None:
            kwargs["metadata"] = self.metadata
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            "form_class": RegexField,
            "regex": re.compile("^[A-Z]{2,3}$"),
            "max_length": self.max_length,
            "error_messages": {
                "invalid": _(
                    "Enter valid initials. Must be 2-3 letters, all "
                    "in uppercase and no spaces."
                )
            },
        }
        defaults.update(kwargs)
        return super(InitialsField, self).formfield(**defaults)
