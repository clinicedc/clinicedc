from django.conf import settings
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from edc_utils.text import convert_php_dateformat

from ..utils import get_ae_model


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

    def get_readonly_fields(self, request, obj=None) -> tuple:
        fields = super().get_readonly_fields(request, obj=obj)
        if obj:
            fields += ("ae_initial",)
        return fields

    def initial_ae(self, obj):
        """Returns a shortened action identifier."""
        if obj.ae_initial:
            url_name = "_".join(obj.ae_initial._meta.label_lower.split("."))
            namespace = self.admin_site.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return format_html(  # nosec B703, B308
                '<a data-toggle="tooltip" title="go to AE initial" href="{}?q={}">{}</a>',
                mark_safe(url),  # nosec B703, B308
                obj.ae_initial.action_identifier,
                obj.ae_initial.identifier,
            )
        return None


class AdverseEventModelAdminMixin:
    @staticmethod
    def user(obj):
        """Returns formatted usernames and creation/modification dates."""
        return format_html(
            "<BR>".join(
                [
                    obj.user_created,
                    obj.created.strftime(convert_php_dateformat(settings.SHORT_DATE_FORMAT)),
                    obj.user_modified,
                    obj.modified.strftime(convert_php_dateformat(settings.SHORT_DATE_FORMAT)),
                ]
            )
        )

    def follow_up_reports(self, ae_initial):
        """Returns a formatted list of links to AE Follow up reports."""
        followups = []
        ae_followup_model_cls = get_ae_model("aefollowup")
        ae_susar_model_cls = get_ae_model("aesusar")
        for ae_followup in ae_followup_model_cls.objects.filter(
            related_action_item=ae_initial.action_item
        ):
            url = self.get_changelist_url(ae_followup)
            report_datetime = ae_followup.report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            followups.append(
                f'<a title="go to AE follow up report for '
                f'{report_datetime}" '
                f'href="{url}?q={ae_initial.action_identifier}">'
                f"<span nowrap>{ae_followup.identifier}</span></a>"
            )
        for ae_susar in ae_susar_model_cls.objects.filter(
            related_action_item=ae_initial.action_item
        ):
            url = self.get_changelist_url(ae_susar)
            report_datetime = ae_susar.report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            followups.append(
                f'<a title="go to AE SUSAR report for '
                f'{report_datetime}" '
                f'href="{url}?q={ae_initial.action_identifier}">'
                f"<span nowrap>{ae_susar.identifier} (SUSAR)</span></a>"
            )
        if followups:
            return format_html("<BR>".join(followups))
        return None

    def get_changelist_url(self, obj):
        url_name = "_".join(obj._meta.label_lower.split("."))
        namespace = self.admin_site.name
        return reverse(f"{namespace}:{url_name}_changelist")
