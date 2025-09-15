from django.conf import settings
from django.contrib.admin import display
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from edc_utils.text import convert_php_dateformat

from ..utils import get_ae_model
from .utils import ColumnItem


class NonAeInitialModelAdminMixin:
    add_form_template: str = "edc_adverse_event/admin/change_form.html"
    change_list_template = "edc_adverse_event/admin/change_list.html"
    change_form_template = "edc_adverse_event/admin/change_form.html"

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
    add_form_template: str = "edc_adverse_event/admin/change_form.html"
    change_list_template = "edc_adverse_event/admin/change_list.html"
    change_form_template = "edc_adverse_event/admin/change_form.html"

    @display(description="subject identifier", ordering="subject_identifier")
    def subject_identifier_column(self, obj=None):
        return format_html(
            "{subject_identifier}<BR>{action_identifier}",
            subject_identifier=obj.subject_identifier,
            action_identifier=obj.action_identifier.upper()[-9:],
        )

    @display(description="User", ordering="user_created")
    def user(self, obj=None):
        """Returns formatted usernames and creation/modification dates."""
        return format_html(
            "{}",
            mark_safe(  # noqa: S308
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
                ),
            ),  # nosec B703, B308
        )

    @display(description="Documents")
    def documents_column(self, model_obj):
        """Returns a formatted list of links to AE Followup reports."""
        column_items: list[ColumnItem] = []
        ae_followup_model_cls = get_ae_model("aefollowup")
        ae_susar_model_cls = get_ae_model("aesusar")
        death_report_model_cls = get_ae_model("deathreport")

        try:
            ae_initial = model_obj.ae_initial
        except AttributeError:
            ae_initial = model_obj
        column_items.append(
            ColumnItem(self, ae_initial, ae_initial.action_identifier, "ae_start_date")
        )

        try:
            death_report = death_report_model_cls.objects.get(
                subject_identifier=ae_initial.subject_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            column_items.append(
                ColumnItem(
                    self,
                    death_report,
                    death_report.subject_identifier,
                    "death_datetime",
                )
            )
        for ae_followup in ae_followup_model_cls.objects.filter(
            related_action_item=ae_initial.action_item
        ):
            column_items.append(
                ColumnItem(
                    self,
                    ae_followup,
                    ae_followup.ae_initial.action_identifier,
                    "outcome_date",
                )
            )
        for ae_susar in ae_susar_model_cls.objects.filter(
            related_action_item=ae_initial.action_item
        ):
            column_items.append(
                ColumnItem(self, ae_susar, ae_susar.ae_initial.action_identifier)
            )
        # order
        sorted(column_items, reverse=True)
        # render
        html = "<table><tr><td>"
        html += "</td><tr><td>".join([c.anchor for c in column_items])
        html += "</td></td></table>"
        return format_html(
            "{}",
            mark_safe(html),  # nosec B703, B308
        )
