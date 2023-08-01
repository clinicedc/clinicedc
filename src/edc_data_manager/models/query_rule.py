from uuid import uuid4

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.deletion import PROTECT
from django.template.loader import render_to_string
from django.utils.functional import lazy
from edc_constants.constants import NORMAL
from edc_dashboard.utils import get_bootstrap_version
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_visit_schedule.constants import DAYS, HOURS, MONTHS, WEEKS

from ..choices import QUERY_PRIORITY
from ..site_data_manager import site_data_manager
from .data_dictionary import DataDictionary, DataDictionaryManager
from .query_visit_schedule import QueryVisitSchedule
from .requisition_panel import RequisitionPanel
from .user import DataManagerUser, QueryUser


class QueryRuleError(Exception):
    pass


class QueryRuleManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)


def get_rule_handler_choices(model_name=None):
    choices = []
    for rule_handler in site_data_manager.get_rule_handlers(model_name=model_name):
        choices.append((rule_handler.name, rule_handler.display_name))
    return tuple(choices) or (
        (DEFAULT_RULE_HANDLER, DEFAULT_RULE_HANDLER.replace("_", " ").title()),
    )


REPORT_DATE = "report_datetime"
DRAWN_DATE = "drawn_datetime"

DATE_CHOICES = (
    (REPORT_DATE, "Report datetime (visit report)"),
    (DRAWN_DATE, "Specimen draw date (requisition)"),
)

UNITS = ((HOURS, "Hours"), (DAYS, "Days"), (WEEKS, "Weeks"), (MONTHS, "Months"))

DEFAULT_RULE_HANDLER = "default"

query_text_template_name = (
    f"edc_data_manager/bootstrap{get_bootstrap_version()}/default_query_text.html"
)


class CrfDataDictionaryManager(DataDictionaryManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(
                model__in=[
                    settings.SUBJECT_REQUISITION_MODEL,
                    settings.SUBJECT_VISIT_MODEL,
                ]
            )
        )


class CrfDataDictionary(DataDictionary):
    objects = CrfDataDictionaryManager()

    class Meta:
        proxy = True
        default_permissions = ("view",)


class VisitDataDictionaryManager(DataDictionaryManager):
    def get_queryset(self):
        return super().get_queryset().filter(model=settings.SUBJECT_VISIT_MODEL)


class VisitDataDictionary(DataDictionary):
    objects = VisitDataDictionaryManager()

    class Meta:
        proxy = True
        default_permissions = ("view",)


class RequisitionDataDictionaryManager(DataDictionaryManager):
    def get_queryset(self):
        return super().get_queryset().filter(model=settings.SUBJECT_REQUISITION_MODEL)


class RequisitionDataDictionary(DataDictionary):
    objects = RequisitionDataDictionaryManager()

    class Meta:
        proxy = True
        default_permissions = ("view",)


class QueryRule(BaseUuidModel):
    active = models.BooleanField(default=True)

    title = models.CharField(max_length=150, unique=True)

    reference_model = models.CharField(max_length=150, null=True, editable=False)

    sender = models.ForeignKey(
        DataManagerUser,
        related_name="+",
        on_delete=PROTECT,
        verbose_name="Query raised by",
    )

    visit_schedule = models.ManyToManyField(
        QueryVisitSchedule,
        verbose_name="Visit",
        related_name="+",
        blank=True,
        help_text="select all that apply",
    )

    visit_schedule_exclude = models.ManyToManyField(
        QueryVisitSchedule,
        verbose_name="Visit (exclude)",
        related_name="+",
        blank=True,
        help_text="select all that apply",
    )

    data_dictionaries = models.ManyToManyField(
        CrfDataDictionary,
        verbose_name="Question(s)",
        related_name="+",
        blank=True,
        help_text="select all that apply",
    )

    sites = models.ManyToManyField(Site, help_text="Leave blank to apply to all.")

    requisition_panel = models.ForeignKey(
        RequisitionPanel,
        verbose_name="Are responses linked to a requisition? If so, which",
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="Requisition will be expected on day of visit.",
    )

    query_text = models.TextField(
        help_text="Generic query text for auto-generated queries.",
        null=True,
        blank=True,
    )

    # TODO: is this the CRF report datetime, for example?
    reference_date = models.CharField(
        max_length=25, choices=DATE_CHOICES, default=REPORT_DATE, editable=False
    )

    # TODO: Does this work? Does this value suggest when to run the ...
    # TODO: ... query relative to the report datetime
    timing = models.IntegerField(verbose_name="Timing", default=48)

    timing_units = models.CharField(
        verbose_name="Units", max_length=25, choices=UNITS, default=HOURS
    )

    query_priority = models.CharField(
        verbose_name="Priority", max_length=25, choices=QUERY_PRIORITY, default=NORMAL
    )

    recipients = models.ManyToManyField(
        QueryUser,
        related_name="+",
        verbose_name="Send to",
        help_text=(
            "Select any additional recipients. Users in the `Site Data Manager` "
            "group are automatically included."
        ),
        blank=True,
    )

    rule_handler_name = models.CharField(
        max_length=150,
        default=DEFAULT_RULE_HANDLER,
        choices=lazy(get_rule_handler_choices, tuple)(),
    )

    reference = models.CharField(max_length=36, default=uuid4, unique=True)

    comment = models.TextField(null=True, blank=True)

    objects = QueryRuleManager()

    history = HistoricalRecords()

    def __str__(self):
        inactive = " (inactive)" if not self.active else ""
        return f"{self.title}{inactive}"

    def save(self, *args, **kwargs):
        self.reference_model = settings.SUBJECT_VISIT_MODEL
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.title,)  # noqa

    natural_key.dependencies = [
        "edc_data_manager.CrfDataDictionary",
        "edc_data_manager.DataManagerUser",
        "edc_data_manager.QueryUser",
        "edc_data_manager.queryvisitschedule",
        "edc_data_manager.RequisitionPanel",
    ]

    @property
    def rendered_query_text(self) -> str:
        context = dict(model=self)
        return render_to_string(template_name=query_text_template_name, context=context)

    @property
    def reference_model_cls(self):
        return django_apps.get_model(self.reference_model)

    @property
    def model_cls(self):
        dct_models = list(set([dd.model for dd in self.data_dictionaries.all()]))
        if len(dct_models) != 1:
            raise QueryRuleError(
                "Multiple models specified. Questions from only one model are allowed."
            )
        return django_apps.get_model(dct_models[0])

    class Meta(BaseUuidModel.Meta):
        ordering = ("title",)
        verbose_name = "Query Rule"
        verbose_name_plural = "Query Rules"
        indexes = [models.Index(fields=["title", "active"])]
