import sys
from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style
from django.conf import settings

style = color_style()

ATTR = 0
MODEL_LABEL = 1


class EdcVisitTrackingAppConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = 'edc_visit_tracking'
    verbose_name = 'Edc Visit Tracking'

    # report_datetime_allowance:
    #   set to not allow CRF report_datetimes to exceed the
    #   visit report_datetime
    #   by more than X days. Set to -1 to ignore
    report_datetime_allowance = 30
    allow_crf_report_datetime_before_visit = False

    # format {app_label: (model_attr, app_label.model_name)}
    # e.g. {'example': ('subject_visit', 'example.subjectvisit')}
    visit_models = {'edc_visit_tracking': (
        'subject_visit', 'edc_visit_tracking.subjectvisit')}
    reason_field = {}

    def ready(self):

        from .signals import visit_tracking_check_in_progress_on_post_save

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        if not self.visit_models:
            sys.stdout.write(style.ERROR(
                'Warning: Visit models not declared. At least one is required. '
                'See AppConfig.visit_models\n'))
        else:
            for options in self.visit_models.values():
                sys.stdout.write(
                    f' * {options[MODEL_LABEL]} uses model attr \'{options[ATTR]}\'\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

#     def visit_model(self, app_label):
#         """Return the visit model for this app_label.
#         """
#         from warnings import warn
#         warn('edc_visit_tracking app_config method visit_model is Deprecated '
#              'in favor of  visit_model_cls.', DeprecationWarning, stacklevel=2)
#         return self.visit_model_cls(app_label)

    def visit_model_cls(self, app_label):
        """Return the visit model for this app_label.
        """
        try:
            visit_model = django_apps.get_model(
                *self.visit_models[app_label][MODEL_LABEL].split('.'))
        except KeyError:
            raise EdcVisitTrackingAppConfigError(
                f'Visit model not specified for \'{app_label}\'. See AppConfig '
                f'for \'edc_visit_tracking\'. Got {self.visit_models}')
        except LookupError:
            raise EdcVisitTrackingAppConfigError(
                'Invalid visit model specified. See AppConfig '
                f'for \'edc_visit_tracking\'. Got {self.visit_models}')
        return visit_model

    def visit_model_attr(self, label_lower):
        """Return the attribute name for models that use the
        visit model for the given app_label.
        """
        app_label, model_name = label_lower.split('.')
        try:
            visit_model_attr = self.visit_models[app_label][ATTR]
        except KeyError as e:
            raise ImproperlyConfigured(
                f'Unable to select visit_model attr given \'{label_lower}\'. '
                f'Got {e}. Expected one of {list(self.visit_models.keys())}. '
                'See \'edc_visit_tracking.AppConfig\'.')
        model = django_apps.get_model(app_label, model_name)
        try:
            getattr(model, visit_model_attr)
        except AttributeError as e:
            raise ImproperlyConfigured(
                f'Invalid visit model attribute \'{visit_model_attr}\' '
                f'specified for model {label_lower}. See AppConfig for '
                f'\'edc_visit_tracking\'. Got {e}')
        return visit_model_attr


if settings.APP_NAME == 'edc_visit_tracking':

    from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from dateutil.relativedelta import MO, TU, WE, TH, FR

    class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):
        reason_field = {'edc_visit_tracking.subjectvisit': 'reason'}

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            'default': dict(days=[MO, TU, WE, TH, FR],
                            slots=[100, 100, 100, 100, 100])}
