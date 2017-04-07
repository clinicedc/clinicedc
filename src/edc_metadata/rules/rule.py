from django.apps import apps as django_apps
from django.core.exceptions import (
    ObjectDoesNotExist, FieldError, MultipleObjectsReturned)

from ..constants import DO_NOTHING
from .exceptions import RuleError


class Rule:

    def __init__(self, logic, **kwargs):
        self.source_model = None  # set by metaclass
        self.name = None  # set by metaclass
        self.group = None  # set by metaclass
        self.app_label = None  # set by metaclass
        self.logic = logic

    def __repr__(self):
        return '<{}.rule_groups.{}: {}>'.format(self.app_label, self.group, self.name)

    def run(self, visit):
        """Runs the rule for each model in target_models and updates
        metadata if the model instance does not exist.
        """
        try:
            app_config = django_apps.get_app_config('edc_registration')
            registered_subject = app_config.model.objects.get(
                subject_identifier=visit.subject_identifier)
        except app_config.model.DoesNotExist:
            registered_subject = None
        source_obj = None
        source_qs = None
        if self.source_model:
            source_model = django_apps.get_model(*self.source_model)
            try:
                source_obj = source_model.objects.get_for_visit(visit)
            except source_model.DoesNotExist:
                source_obj = None
            except MultipleObjectsReturned:
                source_obj = source_model.objects.filter_for_visit(
                    visit).order_by('created').last()
            except AttributeError as e:
                if 'get_for_visit' not in str(e):
                    raise RuleError(
                        '{} See \'{}\'.'.format(
                            str(e), source_model._meta.label_lower))
                source_obj = visit
            try:
                source_qs = source_model.objects.filter(
                    subject_identifier=visit.subject_identifier)
            except FieldError:
                source_qs = source_model.objects.get_for_subject_identifier(
                    visit.subject_identifier)
        for target_model in self.target_models:
            target_model = django_apps.get_model(*target_model.split('.'))
            if self.runif(visit):
                if self.source_model and not source_obj:
                    pass  # without source_obj, predicate will fail
                else:
                    self.run_rules(
                        target_model, visit, registered_subject, source_obj, source_qs)

    def run_rules(self, target_model, visit, *args):
        if target_model._meta.label_lower == visit._meta.label_lower:
            raise RuleError(
                'Target model and visit model are the same. Got {}=={}'.format(
                    target_model._meta.label_lower, visit._meta.label_lower))
        try:
            target_model.objects.get_for_visit(visit)
        except target_model.DoesNotExist:
            entry_status = self.evaluate(visit, *args)
            try:
                visit.run_rules_for_model(
                    target_model._meta.label_lower,
                    entry_status=entry_status)
            except ObjectDoesNotExist:
                pass
        except AttributeError as e:
            if 'get_for_visit' in str(e):
                raise RuleError(
                    'An exception was raised for target model \'{}\'. '
                    'Got {}'.format(
                        target_model._meta.label_lower,
                        str(e)))
            else:
                raise RuleError(str(e))

    def runif(self, visit, **kwargs):
        """May be overridden to run only on a condition.
        """
        return True

    def evaluate(self, visit, *args):
        """ Evaluates the predicate function and returns a result.
        """
        result = None
        try:
            if self.logic.predicate(visit, *args):
                if self.logic.consequence != DO_NOTHING:
                    result = self.logic.consequence
            else:
                if self.logic.alternative != DO_NOTHING:
                    result = self.logic.alternative
        except Exception as e:
            raise RuleError(
                'An exception was raised when running rule {}. Got {}'.format(self, str(e)))
        return result

    @property
    def __doc__(self):
        return self.logic.predicate.__doc__ or "missing docstring for {}".format(self.logic.predicate)
