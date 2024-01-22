from django.utils.translation import gettext_lazy as _

__all__ = ["site_fieldset_tuple"]

site_fieldset_tuple: tuple[str, dict[str, tuple[str, ...]]] = (
    _("Site"),
    {"classes": ("collapse",), "fields": ["site"]},
)
