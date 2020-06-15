from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext as _
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_dashboard.url_names import url_names
from edc_model_admin import (
    ModelAdminNextUrlRedirectMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    TemplatesModelAdminMixin,
)
from edc_notification import NotificationModelAdminMixin
from edc_registration.models import RegisteredSubject


class ModelAdminSubjectDashboardMixin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,
    NotificationModelAdminMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
):

    date_hierarchy = "modified"
    empty_value_display = "-"
    list_per_page = 10
    subject_dashboard_url_name = "subject_dashboard_url"
    subject_listboard_url_name = "subject_listboard_url"
    show_cancel = True
    show_dashboard_in_list_display_pos = None

    def get_subject_dashboard_url_name(self):
        return url_names.get(self.subject_dashboard_url_name)

    def get_subject_dashboard_url_kwargs(self, obj):
        return dict(subject_identifier=obj.subject_identifier)

    def get_subject_listboard_url_name(self):
        return url_names.get(self.subject_listboard_url_name)

    def get_post_url_on_delete_name(self, *args):
        return self.get_subject_dashboard_url_name()

    def post_url_on_delete_kwargs(self, request, obj):
        return self.get_subject_dashboard_url_kwargs(obj)

    def dashboard(self, obj=None, label=None):
        url = reverse(
            self.get_subject_dashboard_url_name(),
            kwargs=self.get_subject_dashboard_url_kwargs(obj),
        )
        context = dict(title=_("Go to subject's dashboard"), url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if self.show_dashboard_in_list_display_pos is not None:
            list_display = list(list_display)
            if self.dashboard not in list_display:
                list_display.insert(
                    self.show_dashboard_in_list_display_pos, self.dashboard
                )
        return list_display

    def view_on_site(self, obj):
        try:
            RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
        except ObjectDoesNotExist:
            url = reverse(self.get_subject_listboard_url_name())
        else:
            try:
                url = reverse(
                    self.get_subject_dashboard_url_name(),
                    kwargs=self.get_subject_dashboard_url_kwargs(obj),
                )
            except NoReverseMatch as e:
                if callable(super().view_on_site):
                    url = super().view_on_site(obj)
                else:
                    raise NoReverseMatch(
                        f"{e}. See subject_dashboard_url_name for {repr(self)}."
                    )
        return url
