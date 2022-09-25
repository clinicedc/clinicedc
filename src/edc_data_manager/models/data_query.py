from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.deletion import PROTECT
from django.template.loader import render_to_string
from django.urls.base import reverse
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_constants.constants import (
    CLOSED,
    FEEDBACK,
    HIGH_PRIORITY,
    NEW,
    NORMAL,
    OPEN,
    RESOLVED,
)
from edc_dashboard.url_names import InvalidUrlName, url_names
from edc_dashboard.utils import get_bootstrap_version
from edc_model.models import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils.date import get_utcnow
from edc_visit_tracking.utils import get_related_visit_model_cls

from ..action_items import DATA_QUERY_ACTION
from ..constants import AUTO_RESOLVED, CLOSED_WITH_ACTION
from .data_dictionary import DataDictionary
from .query_subject import QuerySubject
from .query_visit_schedule import QueryVisitSchedule
from .requisition_panel import RequisitionPanel
from .user import DataManagerUser, QueryUser

RESPONSE_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (FEEDBACK, "Feedback, awaiting data manager"),
    (RESOLVED, "Resolved"),
)


DM_STATUS = (
    (OPEN, "Open, awaiting site"),
    (CLOSED, "Closed"),
    (CLOSED_WITH_ACTION, "Closed, with plan of action"),
)

QUERY_PRIORITY = ((HIGH_PRIORITY, "High"), (NORMAL, "Normal"))


class DataQuery(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = DATA_QUERY_ACTION

    report_datetime = models.DateTimeField(verbose_name="Query date", default=get_utcnow)

    subject_identifier = models.CharField(max_length=50, null=True, editable=False)

    title = models.CharField(max_length=150, null=True, blank=False)

    sender = models.ForeignKey(
        DataManagerUser,
        related_name="+",
        on_delete=PROTECT,
        verbose_name="Query raised by",
        help_text="Select a name from the list",
    )

    recipients = models.ManyToManyField(
        QueryUser,
        related_name="+",
        verbose_name="Sent to",
        help_text=(
            "Select any additional recipients. Users in the `Site Data Manager` "
            "group are automatically included."
        ),
        blank=True,
    )

    registered_subject = models.ForeignKey(
        QuerySubject,
        verbose_name="Subject Identifier",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    query_priority = models.CharField(
        verbose_name="Priority", max_length=25, choices=QUERY_PRIORITY, default=NORMAL
    )

    visit_schedule = models.ForeignKey(
        QueryVisitSchedule,
        verbose_name="Visit",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    visit_code_sequence = models.IntegerField(
        verbose_name="Visit code sequence",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        null=True,
        blank=True,
        help_text=(
            "Defaults to '0'. For example, when combined with the "
            "visit code `1000` would make `1000.0`."
        ),
    )

    timepoint = models.DecimalField(null=True, decimal_places=1, max_digits=6)

    data_dictionaries = models.ManyToManyField(
        DataDictionary,
        verbose_name="CRF question(s)",
        blank=True,
        help_text="select all that apply",
    )

    requisition_panel = models.ForeignKey(
        RequisitionPanel,
        verbose_name="Are responses linked to a requisition? If so, which",
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="Requisition will be expected on day of visit.",
    )

    query_text = models.TextField(help_text="Describe the query in detail.")

    site_resolved_datetime = models.DateTimeField(
        verbose_name="Site resolved on", null=True, blank=True
    )

    site_response_text = models.TextField(null=True, blank=True)

    site_response_status = models.CharField(
        verbose_name="Site status", max_length=25, choices=RESPONSE_STATUS, default=NEW
    )

    status = models.CharField(
        verbose_name="DM status", max_length=25, choices=DM_STATUS, default=OPEN
    )

    dm_user = models.ForeignKey(
        DataManagerUser,
        verbose_name="DM resolved by",
        related_name="dm_user",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="select a name from the list",
    )

    resolved_datetime = models.DateTimeField(
        verbose_name="DM resolved on", null=True, blank=True
    )

    auto_resolved = models.BooleanField(default=False)

    plan_of_action = models.TextField(
        null=True, blank=True, help_text="If required, provide a plan of action"
    )

    missed_visit = models.BooleanField(
        verbose_name="Visit reported as missed",
        default=False,
        help_text="If visit/timepoint was missed, data is not expected",
    )

    locked = models.BooleanField(
        default=False,
        help_text="If locked, this query will NEVER be reopened.",
    )

    locked_reason = models.TextField(
        verbose_name="Reason query locked",
        null=True,
        blank=True,
        help_text="If required, the reason the query cannot be resolved.",
    )

    rule_generated = models.BooleanField(
        default=False, help_text="This query was auto-generated by a query rule."
    )

    rule_reference = models.CharField(
        verbose_name="Query rule reference", max_length=150, null=True, default=uuid4
    )

    on_site = CurrentSiteManager()

    objects = models.Manager()

    def __str__(self):
        return f"{self.action_identifier[-9:]}, {self.status}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.registered_subject.subject_identifier
        self.try_to_resolve_auto_generated_query()
        super().save(*args, **kwargs)

    def try_to_resolve_auto_generated_query(self):
        if (
            not self.dm_resolved
            and self.rule_generated
            and self.site_response_status == RESOLVED
            and self.site_response_text
            and self.site_response_text.strip() == AUTO_RESOLVED
        ):
            self.status = CLOSED
            self.resolved_datetime = get_utcnow()
            self.dm_user = self.sender

    @property
    def dm_resolved(self):
        return self.status in [CLOSED, CLOSED_WITH_ACTION]

    @property
    def site_resolved(self):
        return self.site_response_status == RESOLVED

    def form_and_numbers_to_string(self):
        ret = []
        model_verbose_names = [
            o.model_verbose_name for o in self.data_dictionaries.all().order_by("model")
        ]
        model_verbose_names = list(set(model_verbose_names))
        for model_verbose_name in model_verbose_names:
            numbers = [
                str(o.number)
                for o in self.data_dictionaries.filter(
                    model_verbose_name=model_verbose_name
                ).order_by("number")
            ]
            numbers = ", ".join(numbers)
            ret.append((model_verbose_name, numbers))
        return ret

    def get_action_item_display_name(self):
        pass

    def get_action_item_reason(self):
        try:
            url = url_names.get("subject_dashboard_url")
        except InvalidUrlName:
            visit_href = "#"
        else:
            try:
                visit = get_related_visit_model_cls().objects.get(
                    subject_identifier=self.registered_subject.subject_identifier,
                    visit_schedule_name=self.visit_schedule.visit_schedule_name,
                    schedule_name=self.visit_schedule.schedule_name,
                    visit_code=self.visit_schedule.visit_code,
                    visit_code_sequence=self.visit_code_sequence,
                )
            except ObjectDoesNotExist:
                visit_href = "#"
            except AttributeError as e:
                if (
                    "visit_schedule_name" not in str(e)
                    and "schedule_name" not in str(e)
                    and "visit_code" not in str(e)
                ):
                    raise
                visit_href = "#"
            else:
                visit_href = reverse(
                    url,
                    kwargs=dict(
                        appointment=str(visit.appointment.id),
                        subject_identifier=self.registered_subject.subject_identifier,
                    ),
                )

        template_name = (
            f"edc_data_manager/bootstrap{get_bootstrap_version()}/" f"columns/query_text.html"
        )
        context = dict(
            form_and_numbers=self.form_and_numbers_to_string(),
            query_priority=self.query_priority,
            query_priority_display=self.get_query_priority_display(),
            query_text=self.query_text,
            questions=self.data_dictionaries.all().order_by("model", "number"),
            report_datetime=self.report_datetime,
            requisition_panel=self.requisition_panel,
            resolved_datetime=self.resolved_datetime,
            site_resolved_datetime=self.site_resolved_datetime,
            site_response_text=self.site_response_text,
            site_response_status=self.get_site_response_status_display(),
            status=self.status,
            dm_user=self.dm_user,
            title=self.title,
            visit_schedule=self.visit_schedule,
            visit_href=visit_href,
        )
        return render_to_string(template_name, context=context)

    @property
    def model_names(self):
        model_names = list(set([dd.model for dd in self.data_dictionaries.all()]))
        return "|".join(model_names)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Data Query"
        verbose_name_plural = "Data Queries"
        unique_together = ["registered_subject", "rule_reference", "visit_schedule"]
        indexes = [
            models.Index(
                fields=[
                    "subject_identifier",
                    "action_identifier",
                    "title",
                    "rule_reference",
                    "registered_subject",
                    "visit_schedule",
                ]
            )
        ]
