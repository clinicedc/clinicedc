import arrow
import sys

from dateutil.relativedelta import relativedelta

from django.apps import AppConfig as DjangoAppConfig
from django.core.exceptions import ImproperlyConfigured

from edc_protocol.cap import ALL_SITES
from edc_protocol.exceptions import SubjectTypeCapError

from .cap import Cap
from .subject_type import SubjectType


class ArrowObject:
    def __init__(self, open_dt, close_dt):
        self.ropen = arrow.Arrow.fromdatetime(open_dt, open_dt.tzinfo).to('utc')
        self.rclose = arrow.Arrow.fromdatetime(close_dt, close_dt.tzinfo).to('utc')


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
        SubjectType('subject', 'Research Subjects', Cap(
            model_name='edc_example.enrollment', max_subjects=9999)),
        SubjectType('subject', 'Research Subjects', Cap(
            model_name='edc_example.enrollmentthree', max_subjects=5))
    ]
    study_open_datetime = arrow.utcnow().floor('hour') - relativedelta(years=1)
    study_close_datetime = arrow.utcnow().ceil('hour')

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' * {}: {}.\n'.format(self.protocol, self.protocol_name))

        self.rstudy_open = arrow.Arrow.fromdatetime(
            self.study_open_datetime, self.study_open_datetime.tzinfo).to('utc').floor('hour')
        self.rstudy_close = arrow.Arrow.fromdatetime(
            self.study_close_datetime, self.study_close_datetime.tzinfo).to('utc').ceil('hour')

        self.study_open_datetime = self.rstudy_open.datetime
        self.study_close_datetime = self.rstudy_close.datetime

        sys.stdout.write(' * Study opening date: {}\n'.format(
            self.study_open_datetime.strftime('%Y-%m-%d %Z')))
        sys.stdout.write(' * Expected study closing date: {}\n'.format(
            self.study_close_datetime.strftime('%Y-%m-%d %Z')))
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

    @property
    def arrow(self):
        return ArrowObject(self.study_open_datetime, self.study_close_datetime)
