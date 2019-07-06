from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import RESOLVED, OPEN
from edc_visit_tracking.models import get_visit_tracking_model

from ..models import DataQuery


class ModelHandlerError(Exception):
    pass


class SimpleHandler:

    """Called by the RuleRunner.

    Handles a single rule instance by either creating a
    new data query, resolving an existing data query,
    or doing nothing.
    """

    name = "default"
    display_name = "Default"

    def __init__(self, registered_subject=None, visit_schedule=None, rule=None):
        self._field_values = {}
        self._model_obj = None
        self._visit_obj = None
        self._recipients = None
        self._resolved = None
        self.created_counter = 0
        self.model_cls = rule.query_rule.model_cls
        self.registered_subject = registered_subject
        self.subject_identifier = registered_subject.subject_identifier
        self.resolved_counter = 0
        self.rule = rule
        self.data_dictionaries = self.rule.query_rule.data_dictionaries.all()
        self.recipients = self.rule.query_rule.recipients.all()
        self.visit_schedule = visit_schedule

    def run(self):
        # resolve an existing data query, if it exists
        if self.model_obj and self.resolved:
            self.data_query = self.get_or_create_data_query(get_only=True)
            if self.data_query:
                self.resolve_existing_query()
        else:
            self.data_query = self.get_or_create_data_query()
            if self.model_obj and not self.resolved:
                if self.data_query.site_resolved and not self.data_query.tcc_resolved:
                    self.reopen_existing_query()

    @property
    def resolved(self):
        if self._resolved is None:
            required_fields = []
            for field_name, field_value in self.field_values.items():
                if not field_value:
                    required_fields.append(field_name)
            self._resolved = not required_fields
        return self._resolved

    @property
    def field_values(self):
        if not self._field_values:
            for data_dictionary in self.data_dictionaries:
                if self.model_obj and data_dictionary.field_name:
                    self._field_values.update(
                        {
                            data_dictionary.field_name: getattr(
                                self.model_obj, data_dictionary.field_name, None
                            )
                        }
                    )
        return self._field_values

    def resolve_existing_query(self):
        if self.data_query:
            site_response_text = (self.data_query.site_response_text or "").replace(
                "[auto-resolved]", ""
            )
            self.data_query.site_response_text = f"{site_response_text} [auto-resolved]"
            self.data_query.site_resolved_datetime = self.model_obj.modified
            self.data_query.site_response_status = RESOLVED
            self.data_query.resolved_datetime = self.model_obj.modified
            self.data_query.tcc_user = self.rule.query_rule.sender
            self.data_query.status = RESOLVED
            self.data_query.save()
            self.resolved_counter = 1
        return self.data_query

    def reopen_existing_query(self):
        if self.data_query:
            self.data_query.site_response_text.replace("[auto-resolved]", "")
            self.data_query.site_resolved_datetime = None
            self.data_query.site_response_status = OPEN
            self.data_query.save()

    @property
    def visit_obj(self):
        """Returns a visit model instance or None for this
        subject_identifier and visit schedule timepoint.
        """
        if not self._visit_obj:
            try:
                self._visit_obj = get_visit_tracking_model().objects.get(
                    appointment__visit_schedule_name=self.visit_schedule.visit_schedule_name,
                    appointment__schedule_name=self.visit_schedule.schedule_name,
                    appointment__visit_code=self.visit_schedule.visit_code,
                    appointment__visit_code_sequence=0,
                    appointment__subject_identifier=self.subject_identifier,
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
                        subject_identifier=self.subject_identifier
                    )
        return self._model_obj

    def get_or_create_data_query(self, get_only=None):
        """Returns a data_query.

        If one does not exist it will be created.
        """
        try:
            data_query = DataQuery.objects.get(
                subject_identifier=self.registered_subject.subject_identifier,
                rule_generated=True,
                rule_reference=self.rule.query_rule.reference,
                registered_subject=self.registered_subject,
                visit_schedule=self.visit_schedule,
                site=self.registered_subject.site,
            )
        except ObjectDoesNotExist:
            data_query = None
            if not get_only:
                data_query = DataQuery(
                    query_priority=self.rule.query_rule.query_priority,
                    query_text=self.rule.query_rule.query_text,
                    registered_subject=self.registered_subject,
                    requisition_panel=self.rule.query_rule.requisition_panel,
                    rule_generated=True,
                    rule_reference=str(self.rule.query_rule.reference),
                    sender=self.rule.query_rule.sender,
                    site=self.registered_subject.site,
                    subject_identifier=self.registered_subject.subject_identifier,
                    title=self.rule.query_rule.title,
                    visit_schedule=self.visit_schedule,
                )
                data_query.save()
                for data_dictionary in self.data_dictionaries:
                    data_query.data_dictionaries.add(data_dictionary)
                for recipient in self.recipients:
                    data_query.recipients.add(recipient)
                self.created_counter = 1
        return data_query


class ModelHandler(SimpleHandler):
    model_name = None
    name = None
    display_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.model_cls._meta.label_lower != self.model_name:
            raise ModelHandlerError(
                f"Invalid model class for rule runner. Expected {self.model_name}. "
                f"Got {self.model_cls._meta.label_lower}"
            )
