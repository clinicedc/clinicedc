from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from ..constants import DO_NOTHING

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
        predicate = self.logic.predicate(**options)
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
