import sys
from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig
from django.core.exceptions import ImproperlyConfigured


ATTR = 0
MODEL_LABEL = 1


class AppConfig(DjangoAppConfig):
    name = 'edc_visit_tracking'
    verbose_name = 'Edc Visit Tracking'

    # report_datetime_allowance:
    #   set to not allow CRF report_datetimes to exceed the visit report_datetime
    #   by more than X days. Set to -1 to ignore
    report_datetime_allowance = 30

    # format {app_label: (model_attr, app_label.model_name)}
    # e.g. {'example': ('subject_visit', 'example.subjectvisit')}
    visit_models = {'edc_example': ('subject_visit', 'edc_example.subjectvisit')}

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        from .signals import visit_tracking_check_in_progress_on_post_save
        if not self.visit_models:
            raise ImproperlyConfigured('Visit models not declared. See edc_visit_tracking.AppConfig')
        for options in self.visit_models.values():
            sys.stdout.write(' * {} uses model attr \'{}\'\n'.format(options[MODEL_LABEL], options[ATTR]))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def visit_model(self, app_label):
        """Return the visit model for this app_label."""
        try:
            visit_model = django_apps.get_model(
                *self.visit_models[app_label][MODEL_LABEL].split('.'))
        except LookupError as e:
            raise ImproperlyConfigured(
                'Invalid visit model specified. See AppConfig '
                'for \'edc_visit_tracking\'. Got {} {}'.format(str(e), self.visit_models))
        return visit_model

    def visit_model_attr(self, label_lower):
        """Return the attribute name for models that use the visit model for the given app_label."""
        app_label, model_name = label_lower.split('.')
        try:
            visit_model_attr = self.visit_models[app_label][ATTR]
        except KeyError as e:
            raise ImproperlyConfigured(
                'Unable to select visit_model attr given \'{}\'. '
                'Got {}. See \'edc_visit_tracking.AppConfig\'.'.format(label_lower, str(e)))
        model = django_apps.get_model(app_label, model_name)
        try:
            getattr(model, visit_model_attr)
        except AttributeError as e:
            raise ImproperlyConfigured(
                'Invalid visit model attribute \'{}\' specified for model {}. '
                'See AppConfig for \'edc_visit_tracking\'. Got {}'.format(
                    visit_model_attr, label_lower, str(e)))
        return visit_model_attr
