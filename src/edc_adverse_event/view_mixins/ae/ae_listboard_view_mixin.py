from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html
from edc_action_item.model_wrappers import (
    ActionItemModelWrapper as BaseActionItemModelWrapper,
)
from edc_constants.constants import CLOSED, NEW, OPEN
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin
from edc_utils import get_utcnow

from ...constants import AE_INITIAL_ACTION
from ...model_wrappers import AeInitialModelWrapper, DeathReportModelWrapper
from ...pdf_reports import AePdfReport
from ...utils import get_ae_model


class ActionItemModelWrapper(BaseActionItemModelWrapper):
    ae_initial_model_wrapper = AeInitialModelWrapper
    death_report_model_wrapper = DeathReportModelWrapper
    next_url_name = "ae_listboard_url"

    def __init__(self, model_obj=None, **kwargs):
        self._death_report = None
        super().__init__(model_obj=model_obj, **kwargs)

    @property
    def death_report(self):
        if not self._death_report:
            model_cls = django_apps.get_model(self.death_report_model_wrapper.model)
            try:
                self._death_report = self.death_report_model_wrapper(
                    model_obj=model_cls.objects.get(subject_identifier=self.subject_identifier)
                )
            except ObjectDoesNotExist:
                self._death_report = None
        return self._death_report

    @property
    def ae_initial(self):
        return self.ae_initial_model_wrapper(model_obj=self.object.reference_obj)


class AeListboardViewMixin(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):
    pdf_report_cls = AePdfReport

    listboard_back_url = "ae_home_url"
    home_url = "ae_home_url"
    listboard_panel_title = "Adverse Events: AE Initial and Follow-up Reports"
    model_wrapper_cls = ActionItemModelWrapper

    listboard_template = "ae_listboard_template"
    listboard_url = "ae_listboard_url"
    listboard_panel_style = "default"
    listboard_model = "edc_action_item.actionitem"
    listboard_view_permission_codename = "edc_adverse_event.view_ae_listboard"

    listboard_instructions = format_html(
        (
            "To find an initial adverse event report, search on the subject's "
            "study identifier or AE reference number."
        )
        + " <BR>"
        + "To download the printable report, click on the PDF button"
        + " <i class='fas fa-file-pdf fa-fw'></i> "
        + "left of the subject's identifier."
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
            ae_initial_obj = self.ae_initial_model_cls.objects.get(
                action_identifier=action_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            pdf_report = self.get_pdf_report(
                ae_initial=ae_initial_obj,
                subject_identifier=ae_initial_obj.subject_identifier,
                user=self.request.user,
                request=request,
            )
            return pdf_report.render_to_response()
        return None

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context = self.add_url_to_context(
            new_key="ae_home_url", existing_key=self.home_url, context=context
        )
        context["AE_INITIAL_ACTION"] = AE_INITIAL_ACTION
        context["utc_date"] = get_utcnow().date()
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(
            action_type__name__in=self.action_type_names, status__in=[NEW, OPEN, CLOSED]
        )
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

    @property
    def ae_initial_model_cls(self):
        return get_ae_model("aeinitial")

    def get_pdf_report(self, **kwargs) -> AePdfReport:
        pdf_report_cls = getattr(self.ae_initial_model_cls, "pdf_report_cls", None)
        if not pdf_report_cls:
            pdf_report_cls = getattr(self, "pdf_report_cls", None)
        return pdf_report_cls(**kwargs)
