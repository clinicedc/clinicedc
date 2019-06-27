from django.apps import apps as django_apps
from django.conf import settings
from django.db import models
from django.db.models.deletion import PROTECT
from django.template.loader import render_to_string
from edc_constants.constants import NORMAL
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.constants import HOURS, DAYS, WEEKS, MONTHS

from .data_dictionary import DataDictionary
from .data_query import QUERY_PRIORITY
from .query_visit_schedule import QueryVisitSchedule
from .requisition_panel import RequisitionPanel
from .user import DataManagerUser, QueryUser

REPORT_DATE = "report_datetime"
DRAWN_DATE = "drawn_datetime"

DATE_CHOICES = (
    (REPORT_DATE, "Report datetime (visit report)"),
    (DRAWN_DATE, "Specimen draw date (requisition)"),
)

UNITS = ((HOURS, "Hours"), (DAYS, "Days"),
         (WEEKS, "Weeks"), (MONTHS, "Months"))

query_text_template_name = (
    f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/default_query_text.html"
)


class CrfDataDictionaryManager(models.Manager):
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


class VisitDataDictionaryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(model=settings.SUBJECT_VISIT_MODEL)


class VisitDataDictionary(DataDictionary):

    objects = VisitDataDictionaryManager()

    class Meta:
        proxy = True
        default_permissions = ("view",)


class RequisitionDataDictionaryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(model=settings.SUBJECT_REQUISITION_MODEL)


class RequisitionDataDictionary(DataDictionary):

    objects = RequisitionDataDictionaryManager()

    class Meta:
        proxy = True
        default_permissions = ("view",)


class QueryRuleModelMixin(models.Model):

    active = models.BooleanField(default=True)

    title = models.CharField(max_length=150, unique=True)

    reference_model = models.CharField(
        max_length=150, null=True, editable=False)

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

    query_text = models.TextField(
        help_text="Generic query text for auto-generated queries.",
        null=True,
        blank=True,
    )

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
        help_text="select all that apply",
        blank=True,
    )

    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        inactive = " (inactive)" if not self.active else ""
        return f"{self.title}{inactive}"

    @property
    def rendered_query_text(self):
        context = dict(model=self)
        return render_to_string(template_name=query_text_template_name, context=context)

    @property
    def reference_model_cls(self):
        return django_apps.get_model(self.reference_model)

    @property
    def model_classes(self):
        model_classes = []
        models = list(set([dd.model for dd in self.data_dictionaries.all()]))
        for model in models:
            model_classes.append(django_apps.get_model(model))
        return model_classes

    class Meta:
        abstract = True


class RequisitionQueryRule(QueryRuleModelMixin, SiteModelMixin, BaseUuidModel):

    reference_date = models.CharField(
        max_length=25, choices=DATE_CHOICES, default=REPORT_DATE, editable=False
    )

    reference_model = models.CharField(
        max_length=150,
        null=True,
        default=settings.SUBJECT_REQUISITION_MODEL,
        editable=False,
    )

    requisition_panel = models.ForeignKey(
        RequisitionPanel,
        verbose_name="Panel",
        on_delete=PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )

    # on_site = CurrentSiteManager()

    objects = models.Manager()

    history = HistoricalRecords()


class CrfQueryRule(QueryRuleModelMixin, SiteModelMixin, BaseUuidModel):

    reference_date = models.CharField(
        max_length=25, choices=DATE_CHOICES, default=REPORT_DATE
    )

    reference_model = models.CharField(
        max_length=150, null=True, default=settings.SUBJECT_VISIT_MODEL, editable=False
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

    # on_site = CurrentSiteManager()

    objects = models.Manager()

    history = HistoricalRecords()
