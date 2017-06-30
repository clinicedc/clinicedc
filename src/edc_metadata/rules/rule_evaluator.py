from django.apps import apps as django_apps

from ..constants import DO_NOTHING
from .predicate import PredicateError, NoValueError


class RuleEvaluatorError(Exception):
    pass


class RuleEvaluatorRegisterSubjectError(Exception):
    pass


class RuleEvaluator:

    """A class to evaluate a rule.

    Sets self.result to REQUIRED, NOT_REQUIRED or None.
    """

    def __init__(self, logic=None, source_model=None, visit=None, **kwargs):
        self._registered_subject = None
        self._source_object = None
        self.logic = logic
        self.result = None
        self.subject_identifier = visit.subject_identifier
        self.visit = visit
        if source_model:
            self.source_model = django_apps.get_model(*source_model.split('.'))
        else:
            self.source_model = None
        opts = dict(
            visit=self.visit,
            registered_subject=self.registered_subject,
            source_object=self.source_object,
            source_model=self.source_model)
        try:
            predicate = self.logic.predicate(**opts)
        except PredicateError as e:
            raise RuleEvaluatorError(
                f'Rule predicate failed to evaluate. Rule {repr(self)}. Got {e}')
        except NoValueError as e:
            pass
        else:
            if predicate:
                if self.logic.consequence != DO_NOTHING:
                    self.result = self.logic.consequence
            else:
                if self.logic.alternative != DO_NOTHING:
                    self.result = self.logic.alternative

    @property
    def source_object(self):
        """Returns the source model instance or None.

        Raises an exception if source model is missing a required
        manager method, `get_for_visit`.
        """
        if not self._source_object:
            if self.source_model:
                try:
                    self._source_object = self.source_model.objects.get_for_visit(
                        self.visit)
                except self.source_model.DoesNotExist:
                    pass
                except AttributeError as e:
                    raise RuleEvaluatorError(
                        f'Model missing required manager method \'get_for_visit\'. '
                        f'See \'{self.source_model}\'. Got {e}') from e
        return self._source_object

    @property
    def registered_subject_model(self):
        app_config = django_apps.get_app_config('edc_registration')
        return app_config.model

    @property
    def registered_subject(self):
        """Returns a registered subject model instance or raises.
        """
        if not self._registered_subject:
            try:
                self._registered_subject = self.registered_subject_model.objects.get(
                    subject_identifier=self.subject_identifier)
            except self.registered_subject_model.DoesNotExist as e:
                raise RuleEvaluatorRegisterSubjectError(
                    f'Registered subject required for rule {repr(self)}. '
                    f'subject_identifier=\'{self.subject_identifier}\'. Got {e}.')
        return self._registered_subject
