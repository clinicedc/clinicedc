from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _
from edc_dashboard.url_names import url_names
from edc_registration import get_registered_subject_model_cls

if TYPE_CHECKING:
    from edc_registration.models import RegisteredSubject


class ModelAdminDashboardMixin:
    subject_dashboard_url_name = "subject_dashboard_url"
    subject_listboard_url_name = "subject_listboard_url"
    show_dashboard_in_list_display_pos = None
    view_on_site_label = _("Subject dashboard")

    def dashboard(self, obj=None, label=None) -> str:
        url = self.get_subject_dashboard_url(obj=obj)
        if not url:
            url = reverse(
                self.get_subject_dashboard_url_name(obj=obj),
                kwargs=self.get_subject_dashboard_url_kwargs(obj),
            )
        context = dict(title=_("Go to subject's dashboard"), url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

    def get_subject_listboard_url_name(self) -> str:
        return url_names.get(self.subject_listboard_url_name)

    def get_subject_dashboard_url(self, obj=None) -> str | None:
        return None

    def get_subject_dashboard_url_name(self, obj=None) -> str:
        return url_names.get(self.subject_dashboard_url_name)

    def get_subject_dashboard_url_kwargs(self, obj) -> dict:
        return dict(subject_identifier=obj.subject_identifier)

    def get_post_url_on_delete_name(self, *args) -> str:
        return self.get_subject_dashboard_url_name()

    def post_url_on_delete_kwargs(self, request, obj) -> dict:
        return self.get_subject_dashboard_url_kwargs(obj)

    def get_registered_subject(self, obj) -> RegisteredSubject:
        return get_registered_subject_model_cls().objects.get(
            subject_identifier=obj.subject_identifier
        )

    def get_list_display(self, request) -> tuple[str, ...]:
        list_display = super().get_list_display(request)
        if (
            self.show_dashboard_in_list_display_pos is not None
            and self.dashboard not in list_display
        ):
            list_display = list(list_display)
            list_display.insert(self.show_dashboard_in_list_display_pos, self.dashboard)
            list_display = tuple(list_display)
        return list_display

    def view_on_site(self, obj) -> str:
        try:
            self.get_registered_subject(obj)
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
