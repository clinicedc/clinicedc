import arrow

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import RESOLVED, OPEN, NO
from edc_lab.utils import get_requisition_model
from edc_metadata.constants import REQUIRED, KEYED
from edc_metadata.models import RequisitionMetadata, CrfMetadata
from edc_visit_tracking.models import get_subject_visit_model

from ..models import DataQuery


class QueryRuleHandlerError(Exception):
    pass


class RequisitionNotKeyed(Exception):
    pass


class SpecimenNotDrawn(Exception):
    pass


class CrfInspectionFailed(Exception):
    pass


class DoNothingHandler:

    name = "do_nothing"
    display_name = "Do Nothing"

    def __init__(self, **kwargs):
        pass

    def run(self):
        pass


class QueryRuleHandler:

    """Called by the RuleRunner.

    Handles a single rule instance by either creating a
    new data query, resolving an existing data query,
    or doing nothing.
    """

    name = "default"
    display_name = "Default"
    model_name = None

    def __init__(
        self,
        query_rule_obj=None,
        registered_subject=None,
        visit_schedule_obj=None,
        visit_code_sequence=None,
        now=None,
    ):
        self._field_values = {}
        self._model_obj = None
        self._visit_obj = None
        self._recipients = None
        self._requisition_obj = None
        self.created_counter = 0
        self.data_dictionaries = query_rule_obj.data_dictionaries.all()
        self.model_cls = query_rule_obj.model_cls
        self.now = now
        self.query_rule_obj = query_rule_obj
        self.recipients = query_rule_obj.recipients.all()
        self.registered_subject = registered_subject
        self.resolved_counter = 0
        self.visit_schedule_obj = visit_schedule_obj
        self.visit_code_sequence = visit_code_sequence or 0

        if self.model_name and self.model_cls._meta.label_lower != self.model_name:
            raise QueryRuleHandlerError(
                f"Invalid model class for rule runner. Expected {self.model_name}. "
                f"Got {self.model_cls._meta.label_lower}"
            )

    def run(self):
        site_ids = [o.id for o in self.query_rule_obj.sites.all()]
        if not site_ids or settings.SITE_ID in site_ids:
            if self.resolved:
                self.data_query = self.get_or_create_data_query(get_only=True)
                if self.data_query:
                    self.resolve_existing_data_query()
            else:
                self.data_query = self.get_or_create_data_query()
                if self.data_query.site_resolved:
                    self.reopen_existing_data_query()

    @property
    def resolved(self):
        """Returns True if visit_obj is NULL, or the query is not
        yet due, or the combination of field values is correct.

        To customize, try overriding `inspect_model`.
        """
        resolved = True
        if self.visit_obj:
            try:
                self.inspect_requisition()
            except SpecimenNotDrawn:
                pass
            except RequisitionNotKeyed:
                resolved = not self.requisition_is_required
            else:
                if not self.model_obj:
                    resolved = False
                elif self.model_value_is_due:
                    if not self.crf_is_required:
                        resolved = False
                    else:
                        try:
                            self.inspect_model()
                        except CrfInspectionFailed:
                            resolved = False
        return resolved

    def inspect_requisition(self):
        """Raises a RequisitionNotKeyed or SpecimenNotDrawn exception
        if an expected Requisition is not keyed OR if a keyed
        requisition says specimen is not drawn.

        See `resolved`.
        """
        if self.query_rule_obj.requisition_panel:
            if not self.requisition_obj:
                raise RequisitionNotKeyed()
            if self.requisition_obj and self.requisition_obj.is_drawn == NO:
                raise SpecimenNotDrawn()

    def inspect_model(self):
        """Raises an CrfInspectionFailed exception if the combination
        of field values is incorrect.

        (Assumes a NULL field is missing, one with value is not)

        See `resolved`.

        May be overridden.
        """
        for field_name, field_value in self.field_values.items():
            if not field_value:
                raise CrfInspectionFailed(field_name)

    @property
    def requisition_is_required(self):
        """Returns True if a metadata instance of either REQUIRED
        or KEYED exists.
        """
        opts = dict(
            subject_identifier=self.registered_subject.subject_identifier,
            model=get_requisition_model()._meta.label_lower,
            panel_name=self.query_rule_obj.requisition_panel.name,
            visit_schedule_name=self.visit_obj.visit_schedule_name,
            schedule_name=self.visit_obj.schedule_name,
            visit_code=self.visit_obj.visit_code,
            visit_code_sequence=self.visit_obj.visit_code_sequence,
            entry_status__in=[REQUIRED, KEYED],
        )
        exists = RequisitionMetadata.objects.filter(**opts).exists()
        return exists

    @property
    def crf_is_required(self):
        """Returns True if a metadata instance of either REQUIRED
        or KEYED exists.
        """
        return CrfMetadata.objects.filter(
            subject_identifier=self.registered_subject.subject_identifier,
            model=self.query_rule_obj.model_cls._meta.label_lower,
            visit_schedule_name=self.visit_obj.visit_schedule_name,
            schedule_name=self.visit_obj.schedule_name,
            visit_code=self.visit_obj.visit_code,
            visit_code_sequence=self.visit_obj.visit_code_sequence,
            entry_status__in=[REQUIRED, KEYED],
        ).exists()

    @property
    def model_value_is_due(self):
        """Returns True if value is expected relative to the
        timepoint report datetime.

        Returns True if the model is None.

        See fields `timing` and `timing_units`.
        """
        is_due = False
        if self.visit_obj:
            if not self.model_obj:
                is_due = True
            else:
                now = arrow.get(self.now)
                start = arrow.get(self.visit_obj.report_datetime)
                end = arrow.get(self.visit_obj.report_datetime).shift(
                    **{self.query_rule_obj.timing_units: self.query_rule_obj.timing}
                )
                is_due = now >= start and not now.is_between(start, end, "[]")
        return is_due

    @property
    def field_values(self):
        if not self._field_values:
            for data_dictionary in self.data_dictionaries:
                if data_dictionary.field_name:
                    self._field_values.update(
                        {
                            data_dictionary.field_name: getattr(
                                self.model_obj, data_dictionary.field_name, None
                            )
                        }
                    )
        return self._field_values

    def get_field_value(self, field_name):
        """Safely get a model instance value for this query.
        """
        if not self.query_rule_obj.data_dictionaries.filter(
            field_name=field_name
        ).exists():
            field_names = [
                f"{dd.field_name} ({dd.number})"
                for dd in self.query_rule_obj.data_dictionaries.all()
            ]
            raise QueryRuleHandlerError(
                f"Invalid field specified for query. Expected one of {field_names}. "
                f"Got {field_name}."
            )
        return getattr(self.model_obj, field_name)

    @property
    def resolved_datetime(self):
        try:
            resolved_datetime = self.model_obj.modified
        except AttributeError:
            resolved_datetime = self.requisition_obj.modified
        return resolved_datetime

    def resolve_existing_data_query(self):
        """Resolves a data query model instance.
        """
        if self.data_query:
            site_response_text = (self.data_query.site_response_text or "").replace(
                "[auto-resolved]", ""
            )
            self.data_query.site_response_text = f"{site_response_text} [auto-resolved]"
            self.data_query.site_resolved_datetime = self.resolved_datetime
            self.data_query.site_response_status = RESOLVED
            self.data_query.resolved_datetime = self.resolved_datetime
            self.data_query.dm_user = self.query_rule_obj.sender
            self.data_query.status = RESOLVED
            self.data_query.save()
            self.data_query.refresh_from_db()
            self.resolved_counter = 1

    def reopen_existing_data_query(self):
        """Re-opens a data query model instance unless locked.
        """
        if self.data_query and not self.data_query.locked:
            self.data_query.site_response_text.replace("[auto-resolved]", "")
            self.data_query.site_resolved_datetime = None
            self.data_query.site_response_status = OPEN
            self.data_query.resolved_datetime = None
            self.data_query.status = OPEN
            self.data_query.dm_user = None
            self.data_query.save()
            self.data_query.refresh_from_db()

    @property
    def visit_obj(self):
        """Returns a visit model instance or None for this
        subject_identifier and visit schedule timepoint.
        """
        if not self._visit_obj:
            try:
                self._visit_obj = get_subject_visit_model().objects.get(
                    appointment__visit_schedule_name=(
                        self.visit_schedule_obj.visit_schedule_name
                    ),
                    appointment__schedule_name=self.visit_schedule_obj.schedule_name,
                    appointment__visit_code=self.visit_schedule_obj.visit_code,
                    appointment__visit_code_sequence=self.visit_code_sequence,
                    appointment__subject_identifier=(
                        self.registered_subject.subject_identifier
                    ),
                )
            except ObjectDoesNotExist:
                self._visit_obj = None
        return self._visit_obj

    @property
    def model_obj(self):
        """Returns a CRF model instance or None for this
        subject_identifier and visit schedule timepoint.
        """
        if not self._model_obj:
            try:
                self._model_obj = self.model_cls.objects.get(
                    **{f"{self.model_cls.visit_model_attr()}": self.visit_obj}
                )
            except ObjectDoesNotExist:
                pass
            except AttributeError as e:
                if "visit_model_attr" in str(e):
                    self._model_obj = self.model_cls.objects.get(
                        subject_identifier=self.registered_subject.subject_identifier
                    )
        return self._model_obj

    @property
    def requisition_obj(self):
        """Returns a requisition model instance or None.
        """
        if not self._requisition_obj:
            try:
                self._requisition_obj = get_requisition_model().objects.get(
                    **{f"{self.model_cls.visit_model_attr()}": self.visit_obj},
                    panel=self.query_rule_obj.requisition_panel,
                )
            except ObjectDoesNotExist:
                pass
        return self._requisition_obj

    def get_or_create_data_query(self, get_only=None):
        """Returns a data_query.

        If one does not exist it will be created.
        """
        try:
            data_query = DataQuery.objects.get(
                subject_identifier=self.registered_subject.subject_identifier,
                rule_generated=True,
                rule_reference=self.query_rule_obj.reference,
                registered_subject=self.registered_subject,
                visit_schedule=self.visit_schedule_obj,
                site=self.registered_subject.site,
            )
        except ObjectDoesNotExist:
            data_query = None
            if not get_only:
                data_query = DataQuery(
                    query_priority=self.query_rule_obj.query_priority,
                    query_text=self.query_rule_obj.query_text,
                    registered_subject=self.registered_subject,
                    requisition_panel=self.query_rule_obj.requisition_panel,
                    rule_generated=True,
                    rule_reference=str(self.query_rule_obj.reference),
                    sender=self.query_rule_obj.sender,
                    site=self.registered_subject.site,
                    subject_identifier=self.registered_subject.subject_identifier,
                    title=self.query_rule_obj.title,
                    visit_schedule=self.visit_schedule_obj,
                )
                data_query.save()
                for data_dictionary in self.data_dictionaries:
                    data_query.data_dictionaries.add(data_dictionary)
                for recipient in self.recipients:
                    data_query.recipients.add(recipient)
                self.created_counter = 1
        return data_query
