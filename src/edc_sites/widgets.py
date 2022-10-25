from django.contrib.sites.models import Site
from django.forms import ModelChoiceField


class SiteField(ModelChoiceField):
    def __init__(self, label=None, help_text=None, required=None, **kwargs):
        queryset = Site.objects.all().order_by("name")
        label = label or "Which study site is this?"
        help_text = (
            help_text
            or "This question is asked to confirm you are logged in to the correct site."
        )
        required = required or True
        super().__init__(
            queryset, label=label, help_text=help_text, required=required, **kwargs
        )

    def label_from_instance(self, obj):
        return obj.name.replace("_", " ").title
