from __future__ import annotations

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin
from edc_pylabels.models import LabelConfiguration
from edc_pylabels.site_label_configs import site_label_configs
from edc_utils import get_utcnow
from pylabels import Sheet, Specification

from ..models import Stock


@method_decorator(login_required, name="dispatch")
class PrintLabelsView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    stock_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/print_labels.html"
    session_key = "model_pks"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        try:
            _, querystring = self.request.META.get("HTTP_REFERER").split("?")
        except ValueError:
            querystring = ""
        kwargs.update(
            source_changelist_url=self.source_changelist_url,
            source_model_name=Stock._meta.verbose_name,
            label_configurations=LabelConfiguration.objects.all().order_by("name"),
            q=querystring,
        )
        return super().get_context_data(**kwargs)

    @property
    def source_changelist_url(self):
        return reverse(
            f"edc_pharmacy_admin:edc_pharmacy_{self.kwargs.get("model")}_changelist"
        )

    @property
    def model_cls(self):
        return django_apps.get_model(f"edc_pharmacy.{self.kwargs.get("model")}")

    def post(self, request, *args, **kwargs):
        session_uuid = str(kwargs.get("session_uuid"))
        stock_pks = request.session.get(session_uuid, [])
        url = self.source_changelist_url
        if stock_pks:
            queryset: QuerySet[Stock] = self.model_cls.objects.filter(pk__in=stock_pks)
            del request.session[session_uuid]
            label_configuration: LabelConfiguration = LabelConfiguration.objects.get(
                pk=request.POST.get("label_configuration")
            )
            if label_configuration.requires_allocation and queryset.filter(
                allocation__isnull=True
            ):
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        "Unable to print selected stock items. "
                        f"Label format '{label_configuration.name}' may only be used with "
                        "stock items allocated to subjects."
                    ),
                )
                return HttpResponseRedirect(request.META.get("HTTP_REFERER", ""))
            else:
                label_data = [obj for obj in queryset]
                drawing_callable = site_label_configs.get(
                    label_configuration.name
                ).drawing_callable
                specs = Specification(**label_configuration.label_specification.as_dict)
                sheet = Sheet(
                    specs,
                    drawing_callable,
                    border=label_configuration.label_specification.border,
                )
                sheet.add_labels(label_data)
                buffer = sheet.save_to_buffer()
                now = get_utcnow()
                return FileResponse(
                    buffer,
                    as_attachment=True,
                    filename=(
                        f"{label_configuration.name}_{now.strftime("%Y-%m-%d %H:%M")}.pdf"
                    ),
                )
        return HttpResponseRedirect(url)
