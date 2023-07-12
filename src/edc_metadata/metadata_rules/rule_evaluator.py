from __future__ import annotations

from typing import TYPE_CHECKING, Any
from warnings import warn

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from ..constants import DO_NOTHING
from .predicate import NoValueError

if TYPE_CHECKING:
    from edc_registration.models import RegisteredSubject
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ..model_mixins.creates import CreatesMetadataModelMixin
    from .logic import Logic

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass


class RuleEvaluatorError(Exception):
    pass


class RuleEvaluatorRegisterSubjectError(Exception):
    pass


show_edc_metadata_warnings = getattr(settings, "EDC_METADATA_SHOW_NOVALUEERROR_WARNING", False)


class RuleEvaluator:

    """A class to evaluate a rule.

    Sets `self.result` to REQUIRED, NOT_REQUIRED or None.

    Set as a class attribute on Rule.

    Ensure the `model.field` is registered with `site_reference_configs`.

    Note: the predicate, which is a callable, will create a Reference
    model instance if it does not exist. See `ReferenceGetter` in
    `edc_reference`.

    See also RuleGroup and its metaclass.
    """

    def __init__(
        self, logic: Logic = None, related_visit: RelatedVisitModel = None, **kwargs
    ) -> None:
        self._registered_subject: RegisteredSubject | None = None
        self.logic: Logic = logic
        self.result: str | None = None
        self.related_visit = related_visit
        options = dict(
            visit=self.related_visit, registered_subject=self.registered_subject, **kwargs
        )
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
    def registered_subject_model(self) -> Any:
        app_config = django_apps.get_app_config("edc_registration")
        return app_config.model

    @property
    def registered_subject(self) -> Any:
        """Returns a registered subject model instance or raises."""
        if not self._registered_subject:
            try:
                self._registered_subject = self.registered_subject_model.objects.get(
                    subject_identifier=self.related_visit.subject_identifier
                )
            except ObjectDoesNotExist as e:
                raise RuleEvaluatorRegisterSubjectError(
                    f"Registered subject required for rule {repr(self)}. "
                    f"subject_identifier='{self.related_visit.subject_identifier}'. "
                    f"Got {e}."
                )
        return self._registered_subject
