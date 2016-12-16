import sys

from django.apps import AppConfig as DjangoAppConfig
from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow

from .cap import Cap
from .subject_type import SubjectType
from django.core.exceptions import ImproperlyConfigured
from edc_protocol.cap import ALL_SITES
from edc_protocol.exceptions import SubjectTypeCapError
from django.core.management.color import color_style


class AppConfig(DjangoAppConfig):
    name = 'edc_protocol'
    verbose_name = 'Edc Protocol'

    # set with example defaults, you will need to change from your project
    protocol = 'BHP000'
    protocol_number = '000'  # 3 digits, used for identifiers
    protocol_name = 'My Protocol'
    protocol_title = 'My Protocol of Many Things'

    # these attributes are used by the SubjectTypeCapMixin
    subject_types = [
        SubjectType('subject', 'Research Subjects', Cap(model_name='edc_example.enrollment', max_subjects=9999)),
        SubjectType('subject', 'Research Subjects', Cap(model_name='edc_example.enrollmentthree', max_subjects=5))
    ]
    study_open_datetime = get_utcnow() - relativedelta(days=25)
    study_close_datetime = get_utcnow() + relativedelta(days=25)

    def ready(self):
        style = color_style()
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' * {}: {}.\n'.format(self.protocol, self.protocol_name))
        if 'test' in sys.argv:
            sys.stdout.write(
                style.NOTICE(
                    'WARNING! Overwriting AppConfig study_open_datetime and study_close_datetime for tests only. \n'
                    'See EdcProtocolAppConfig\n'))
            duration_delta = relativedelta(self.study_close_datetime, self.study_open_datetime)
            self.study_open_datetime = (get_utcnow() - relativedelta(years=1)) - duration_delta
            self.study_close_datetime = get_utcnow() - relativedelta(years=1)
        sys.stdout.write(' * Study opening date: {}\n'.format(self.study_open_datetime.strftime('%Y-%m-%d')))
        sys.stdout.write(' * Expected study closing date: {}\n'.format(self.study_close_datetime.strftime('%Y-%m-%d')))
        if isinstance(self.subject_types, (list, tuple)):
            unique_labels = {}
            for subject_type in self.subject_types:
                for cap in subject_type.caps.values():
                    if cap.subject_type_name:
                        if cap.subject_type_name != subject_type.name:
                            raise SubjectTypeCapError('Subject type name does not match cap.')
                    else:
                        cap.subject_type_name = subject_type.name
                    label = '{}:{}:{}'.format(cap.subject_type_name, cap.model_name, cap.study_site)
                    if label in unique_labels:
                        raise ImproperlyConfigured('Enrollment cap not unique. Got {}'.format(label))
                    else:
                        unique_labels.update({label: cap})
            self.subject_types = {}
            for label, cap in unique_labels.items():
                self.subject_types.update({label: cap})
        sys.stdout.write(' * Enrollment caps:\n')
        if len(self.subject_types) == 0:
            sys.stdout.write('   * None specified.\n'.format(label, cap.max_subjects))
        else:
            for label, cap in self.subject_types.items():
                sys.stdout.write('   - found {}.\n'.format(cap))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
        sys.stdout.flush()

    def get_cap(self, subject_type_name=None, model_name=None, study_site=None):
        try:
            cap = self.caps['{}:{}:{}'.format(subject_type_name, model_name, study_site)]
        except KeyError:
            try:
                cap = self.caps['{}:{}:{}'.format(subject_type_name, model_name, ALL_SITES)]
            except KeyError as e:
                raise SubjectTypeCapError('Invalid criteria for Cap. Got {}.'.format(str(e)))
        return cap

    @property
    def caps(self):
        return {cap.name: cap for cap in self.subject_types.values()}
