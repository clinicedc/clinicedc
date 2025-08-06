from uuid import uuid4

import pandas as pd
from celery.states import PENDING
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django_pandas.io import read_frame
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin
from edc_utils.celery import celery_is_active, get_task_result

from ..analytics import get_next_scheduled_visit_for_subjects_df
from ..models import StockRequest, StockRequestItem
from ..utils import bulk_create_stock_request_items, get_instock_and_nostock_data


@method_decorator(login_required, name="dispatch")
class PrepareAndReviewStockRequestView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name: str = "edc_pharmacy/stock/stock_request.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        stock_request = StockRequest.objects.get(pk=self.kwargs.get("stock_request"))
        df = get_next_scheduled_visit_for_subjects_df(stock_request)

        # get unallocated stock that appears in a stock request for this location
        df_unallocated_request_items = read_frame(
            StockRequestItem.objects.values(
                "stock_request__request_identifier", "registered_subject__subject_identifier"
            ).filter(stock_request__location=stock_request.location, allocation__isnull=True)
        )
        df_unallocated_request_items.rename(
            columns={
                "registered_subject__subject_identifier": "subject_identifier",
                "stock_request__request_identifier": "request_identifier",
            },
            inplace=True,
        )
        df_unallocated_request_items.reset_index(drop=True, inplace=True)
        df_unallocated_request_items = pd.merge(
            df_unallocated_request_items,
            df[["subject_identifier", "next_visit_code", "next_appt_datetime"]],
            on="subject_identifier",
            how="left",
        )
        df_unallocated_request_items = df_unallocated_request_items[
            df_unallocated_request_items.next_visit_code.notna()
        ]
        df_unallocated_request_items.sort_values(by=["subject_identifier"]).reset_index(
            drop=True, inplace=True
        )

        # exclude unallocated subjects from appts
        df = df[~df.subject_identifier.isin(df_unallocated_request_items.subject_identifier)]
        df.reset_index(drop=True, inplace=True)

        kwargs.update(
            stock_request=stock_request,
            stock_request_items_exist=stock_request.stockrequestitem_set.all().exists(),
            source_model_name=self.model_cls._meta.verbose_name_plural,
            source_changelist_url=self.source_changelist_url,
            rows=0,
            subjects=[],
        )

        if df.empty:
            messages.add_message(
                self.request,
                messages.ERROR,
                (
                    f"No future subject appointments found for {stock_request.location} "
                    f"with this cutoff date. (Site {stock_request.location.site.id})."
                ),
            )
        elif getattr(get_task_result(stock_request), "status", "") == PENDING:
            messages.add_message(
                self.request,
                messages.ERROR,
                (
                    f"Stock request {stock_request.request_identifier} is still processing. "
                    "Please click cancel and check the status column."
                ),
            )
        else:
            df_instock, df_nostock = get_instock_and_nostock_data(stock_request, df)
            session_uuid = str(uuid4())
            nostock_dict = df_nostock[
                [
                    "subject_identifier",
                    "registered_subject_id",
                    "next_visit_code",
                    "next_appt_datetime",
                ]
            ].to_dict("list")
            nostock_dict["stock_qty"] = 0.0
            self.request.session[session_uuid] = nostock_dict

            stock_request_items_exist = stock_request.stockrequestitem_set.all().exists()
            if stock_request_items_exist:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    message=(
                        f"Stock request items already exist for "
                        f"{stock_request._meta.verbose_name} "
                        f"{stock_request.request_identifier}. "
                        "Create has been disabled."
                    ),
                )
            kwargs.update(
                rows=len(df_nostock),
                subjects=df_nostock.subject_identifier.nunique(),
                subjects_excluded_by_stock=len(df_instock.subject_identifier.unique()),
                subjects_excluded_by_request=len(
                    df_unallocated_request_items.subject_identifier.unique()
                ),
                nostock_table=format_html(
                    "{}",
                    mark_safe(
                        df_nostock.to_html(
                            columns=[
                                "subject_identifier",
                                "next_visit_code",
                                "next_appt_datetime",
                            ],
                            index=True,
                            border=0,
                            classes="table table-striped",
                            table_id="my_table",
                        )
                    ),  # nosec B703 B308
                ),
                instock_table=format_html(
                    "{}",
                    mark_safe(
                        df_instock.to_html(
                            columns=[
                                "subject_identifier",
                                "next_visit_code",
                                "next_appt_datetime",
                                "code",
                            ],
                            index=True,
                            border=0,
                            classes="table table-striped",
                            table_id="in_stock_table",
                        )
                    ),  # nosec B703 B308
                ),
                unallocated_table=format_html(
                    "{}",
                    mark_safe(
                        df_unallocated_request_items.to_html(
                            columns=[
                                "subject_identifier",
                                "next_visit_code",
                                "next_appt_datetime",
                                "request_identifier",
                            ],
                            index=True,
                            border=0,
                            classes="table table-striped",
                            table_id="unallocated_table",
                        )
                    ),  # nosec B703 B308
                ),
                session_uuid=session_uuid,
            )
        return super().get_context_data(**kwargs)

    @property
    def source_changelist_url(self):
        return reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")

    @property
    def model_cls(self):
        return django_apps.get_model("edc_pharmacy.stocktransfer")

    def post(self, request, *args, **kwargs):
        session_uuid = request.POST.get("session_uuid")
        stock_request = StockRequest.objects.get(pk=request.POST.get("stock_request"))
        if not request.POST.get("cancel") and session_uuid:
            nostock_dict = request.session[session_uuid]
            if session_uuid:
                del request.session[session_uuid]

            task_id = None
            if not celery_is_active():
                bulk_create_stock_request_items(
                    stock_request.pk, nostock_dict, user_created=request.user.username
                )
            else:
                task = bulk_create_stock_request_items.delay(
                    stock_request.pk, nostock_dict, user_created=request.user.username
                )
                task_id = getattr(task, "id", None)
            obj = StockRequest.objects.get(pk=request.POST.get("stock_request"))
            obj.task_id = task_id
            obj.save(update_fields=["task_id"])

            messages.add_message(
                request,
                messages.SUCCESS,
                (
                    f"Successfully created items for Stock Request "
                    f"{stock_request.request_identifier}"
                ),
            )
            url = f"{self.source_changelist_url}?q={stock_request.request_identifier}"
        else:
            if session_uuid:
                del request.session[session_uuid]
            messages.add_message(
                request,
                messages.INFO,
                "Cancelled. No stock request items were created.",
            )
            url = f"{self.source_changelist_url}"
        return HttpResponseRedirect(url)
