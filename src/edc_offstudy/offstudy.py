from django.apps import apps as django_apps
from django.utils import timezone
from edc_constants.date_constants import EDC_DATETIME_FORMAT
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

NOT_CONSENTED = 'not_consented'
INVALID_OFFSTUDY_DATETIME_CONSENT = 'invalid_offstudy_datetime_consent'
SUBJECT_NOT_REGISTERED = 'not_registered'
OFFSTUDY_DATETIME_BEFORE_DOB = 'offstudy_datetime_before_dob'
INVALID_DOB = 'invalid_dob'
INVALID_VISIT_MODEL = 'invalid_visit_model'
INVALID_CONSENT_MODEL = 'invalid_consent_model'


class OffstudyError(ValidationError):
    pass


class Offstudy:

    def __init__(self, offstudy_model=None, subject_identifier=None,
                 offstudy_datetime=None, **kwargs):
        self._consent_model_cls = None
        self._visit_model_cls = None
        self.subject_identifier = subject_identifier
        self.offstudy_datetime = offstudy_datetime
        self.offstudy_model = offstudy_model
        app_config = django_apps.get_app_config('edc_appointment')
        appointment_model_cls = django_apps.get_model(app_config.get_configuration(
            related_visit_model=self.visit_model_cls._meta.label_lower).model)

        self.registered_or_raise()
        self.consented_or_raise(**kwargs)
        self.offstudy_datetime_or_raise(**kwargs)

        # passes validation, now delete unused "future" appointments
        appointment_model_cls.objects.delete_for_subject_after_date(
            self.subject_identifier, self.offstudy_datetime)

    @property
    def visit_model_cls(self):
        """Returns the visit model class linked to this offstudy
        model by the visit schedule.

        Note: if more than one visit schedule refers to this offstudy
        model, the visit model must be the same for each.
        """
        if not self._visit_model_cls:
            visit_models = []
            for visit_schedule in site_visit_schedules.get_by_offstudy_model(
                    self.offstudy_model):
                for schedule in visit_schedule.schedules.values():
                    visit_models.append(schedule.visit_model_cls)
            visit_models = list(set(visit_models))
            if len(visit_models) != 1:
                raise OffstudyError(
                    'Unable to determine a unique visit model class '
                    f'given offstudy model {self.offstudy_model}.',
                    code=INVALID_VISIT_MODEL)
            self._visit_model_cls = visit_models[0]
        return self._visit_model_cls

    @property
    def consent_model_cls(self):
        """Returns the consent model class linked to this offstudy
        model by the visit schedule.

        Note: if more than one visit schedule refers to this offstudy
        model, the consent model must be the same for each.
        """
        if not self._consent_model_cls:
            consent_models = []
            for visit_schedule in site_visit_schedules.get_by_offstudy_model(
                    self.offstudy_model):
                for schedule in visit_schedule.schedules.values():
                    consent_models.append(schedule.consent_model_cls)
            consent_models = list(set(consent_models))
            if len(consent_models) != 1:
                raise OffstudyError(
                    'Unable to determine a unique consent model class '
                    f'given offstudy model {self.offstudy_model}.',
                    code=INVALID_CONSENT_MODEL)
            self._consent_model_cls = consent_models[0]
        return self._consent_model_cls

    def registered_or_raise(self, **kwargs):
        """Raises an exception if subject is not registered or
        if subject's DoB precedes the offstudy_datetime.
        """
        try:
            obj = RegisteredSubject.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            raise OffstudyError(
                f'Unknown subject. Got {self.subject_identifier}.',
                code=SUBJECT_NOT_REGISTERED)
        else:
            if not obj.dob:
                raise OffstudyError(
                    'Invalid date of birth. Got None',
                    code=INVALID_DOB)
            else:
                if obj.dob > timezone.localdate(self.offstudy_datetime):
                    formatted_date = timezone.localtime(
                        self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
                    raise OffstudyError(
                        f'Invalid off-study date. '
                        f'Off-study date may not precede date of birth. '
                        f'Got \'{formatted_date}\'.',
                        code=OFFSTUDY_DATETIME_BEFORE_DOB)

    def consented_or_raise(self, **kwargs):
        """Raises an exception if subject has not consented.
        """
        if not self.consent_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).exists():
            raise OffstudyError(
                'Unable to take subject off study. Subject has not consented. '
                f'Got {self.subject_identifier}.', code=NOT_CONSENTED)

    def offstudy_datetime_or_raise(self, **kwargs):
        """Raises an exception if offstudy_datetime precedes
        consent_datetime or the last visit_datetime.
        """
        # validate relative to the first consent datetime
        consent = self.consent_model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            consent_datetime__lte=self.offstudy_datetime).order_by(
                'consent_datetime').first()
        if not consent:
            formatted_date = timezone.localtime(
                self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
            raise OffstudyError(
                f'Invalid off-study date. '
                f'Off-study date may not be before the date of consent. '
                f'Got \'{formatted_date}\'.',
                code=INVALID_OFFSTUDY_DATETIME_CONSENT)
        # validate relative to the last visit datetime
        last_visit = self.visit_model_cls.objects.filter(
            subject_identifier=self.subject_identifier).order_by(
                'report_datetime').last()
        if last_visit and (last_visit.report_datetime - self.offstudy_datetime).days > 0:
            formatted_visitdate = timezone.localtime(
                last_visit.report_datetime).strftime(EDC_DATETIME_FORMAT)
            formatted_offstudy = timezone.localtime(
                self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
            raise OffstudyError(
                f'Off-study datetime cannot precede the last visit date. '
                f'Last visit date was on {formatted_visitdate}. '
                f'Got {formatted_offstudy}')
