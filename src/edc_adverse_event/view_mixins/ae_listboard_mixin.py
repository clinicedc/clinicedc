import arrow

from ambition_ae.action_items import AE_INITIAL_ACTION
from ambition_ae.models import AeInitial
from ambition_dashboard.model_wrappers import DeathReportModelWrapper
from ambition_reports.ae_report import AEReport
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from edc_action_item.model_wrappers import (
    ActionItemModelWrapper as BaseActionItemModelWrapper,
)
from edc_dashboard.view_mixins import (
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
)
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ...model_wrappers import AeInitialModelWrapper


class ActionItemModelWrapper(BaseActionItemModelWrapper):

    ae_initial_model_wrapper = AeInitialModelWrapper
    death_report_model = None  # "ambition_prn.deathreport"
    death_report_model_wrapper = DeathReportModelWrapper

    next_url_name = "ae_listboard_url"

    def __init__(self, model_obj=None, **kwargs):
        self._death_report = None
        super().__init__(model_obj=model_obj, **kwargs)

    @property
    def death_report(self):
        if not self._death_report:
            model_cls = django_apps.get_model(self.death_report_model)
            try:
                self._death_report = self.death_report_model_wrapper(
                    model_obj=model_cls.objects.get(
                        subject_identifier=self.subject_identifier
                    )
                )
            except ObjectDoesNotExist:
                self._death_report = None
        return self._death_report

    @property
    def ae_initial(self):
        return self.ae_initial_model_wrapper(model_obj=self.object.reference_obj)


class AeListboardView(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):

    ae_model_cls = AeInitial
    ae_report_cls = AEReport
    listboard_back_url = "ambition_dashboard:ae_home_url"
    listboard_panel_title = _("Adverse Events: AE Initial and Follow-up Reports")
    model_wrapper_cls = ActionItemModelWrapper
    navbar_name = "ambition_dashboard"

    listboard_template = "ae_listboard_template"
    listboard_url = "ae_listboard_url"
    listboard_panel_style = "default"
    listboard_model = "edc_action_item.actionitem"
    listboard_view_permission_codename = "edc_dashboard.view_ae_listboard"
    listboard_instructions = mark_safe(
        _(
            "To find an initial adverse event report, search on the subject's "
            "study identifier or AE reference number."
        )
        + " <BR>"
        + _("To download the printable report, click on the PDF button")
        + " <i class='fas fa-file-pdf fa-fw'></i> "
        + _("left of the subject's identifier.")
    )

    navbar_selected_item = "ae_home"
    ordering = "-report_datetime"
    paginate_by = 25
    search_form_url = "ae_listboard_url"
    action_type_names = [AE_INITIAL_ACTION]

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "parent_action_item__action_identifier",
        "related_action_item__action_identifier",
        "user_created",
        "user_modified",
    ]

    def get(self, request, *args, **kwargs):
        if request.GET.get("pdf"):
            response = self.print_pdf_report(
                action_identifier=self.request.GET.get("pdf"), request=request
            )
            return response or super().get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def print_pdf_report(self, action_identifier=None, request=None):
        try:
            ae_initial = self.ae_model_cls.objects.get(
                action_identifier=action_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            report = self.ae_report_cls(
                ae_initial=ae_initial,
                subject_identifier=ae_initial.subject_identifier,
                user=self.request.user,
                request=request,
            )
            return report.render()
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["AE_INITIAL_ACTION"] = AE_INITIAL_ACTION
        context["utc_date"] = arrow.now().date()
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(action_type__name__in=self.action_type_names)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return options

    def get_updated_queryset(self, queryset):
        pks = []
        for obj in queryset:
            try:
                obj.reference_obj
            except ObjectDoesNotExist:
                pks.append(obj.pk)
        return queryset.exclude(pk__in=pks)
