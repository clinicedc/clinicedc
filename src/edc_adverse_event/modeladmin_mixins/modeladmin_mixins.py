from django.urls.base import reverse
from django.utils.safestring import mark_safe

from ..get_ae_model import get_ae_model
from edc_utils.text import convert_php_dateformat
from django.conf import settings


class NonAeInitialModelAdminMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ae_initial":
            if request.GET.get("ae_initial"):
                kwargs["queryset"] = get_ae_model("aeinitial").objects.filter(
                    id__exact=request.GET.get("ae_initial", 0)
                )
            else:
                kwargs["queryset"] = get_ae_model("aeinitial").objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if obj:
            fields = list(fields) + ["ae_initial"]
        return list(fields)

    def initial_ae(self, obj):
        """Returns a shortened action identifier.
        """
        if obj.ae_initial:
            url_name = "_".join(obj.ae_initial._meta.label_lower.split("."))
            namespace = self.admin_site.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return mark_safe(
                f'<a data-toggle="tooltip" title="go to ae initial report" '
                f'href="{url}?q={obj.ae_initial.action_identifier}">'
                f"{obj.ae_initial.identifier}</a>"
            )
        return None


class AdverseEventModelAdminMixin:
    def user(self, obj):
        """Returns formatted user names and creation/modification dates.
        """
        return mark_safe(
            "<BR>".join(
                [
                    obj.user_created,
                    obj.created.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    ),
                    obj.user_modified,
                    obj.modified.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    ),
                ]
            )
        )
