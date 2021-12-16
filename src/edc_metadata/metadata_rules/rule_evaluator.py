from warnings import warn

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from ..constants import DO_NOTHING
from .predicate import NoValueError


class RuleEvaluatorError(Exception):
    pass


class RuleEvaluatorRegisterSubjectError(Exception):
    pass


show_edc_metadata_warnings = getattr(settings, "EDC_METADATA_SHOW_NOVALUEERROR_WARNING", False)


class RuleEvaluator:

    """A class to evaluate a rule.

    Sets self.result to REQUIRED, NOT_REQUIRED or None.

    Set as a class attribute on Rule.

    Ensure the model.field is registered with `site_reference_configs`.
    See `edc_reference`.
    """

    def __init__(self, logic=None, visit=None, **kwargs):
        self._registered_subject = None
        self.logic = logic
        self.result = None
        self.visit = visit
        options = dict(visit=self.visit, registered_subject=self.registered_subject, **kwargs)
        try:
            predicate = self.logic.predicate(**options)
        except NoValueError as e:
            if show_edc_metadata_warnings:
                warn(
                    f"{str(e)} To ignore set settings."
                    "EDC_METADATA_SHOW_NOVALUEERROR_WARNING=False."
                )
            pass
        else:
            if predicate:
                if self.logic.consequence != DO_NOTHING:
                    self.result = self.logic.consequence
            else:
                if self.logic.alternative != DO_NOTHING:
                    self.result = self.logic.alternative

    @property
    def registered_subject_model(self):
        app_config = django_apps.get_app_config("edc_registration")
        return app_config.model

    @property
    def registered_subject(self):
        """Returns a registered subject model instance or raises."""
        if not self._registered_subject:
            try:
                self._registered_subject = self.registered_subject_model.objects.get(
                    subject_identifier=self.visit.subject_identifier
                )
            except ObjectDoesNotExist as e:
                raise RuleEvaluatorRegisterSubjectError(
                    f"Registered subject required for rule {repr(self)}. "
                    f"subject_identifier='{self.visit.subject_identifier}'. "
                    f"Got {e}."
                )
        return self._registered_subject
