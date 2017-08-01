import arrow
import sys

from dateutil.relativedelta import relativedelta

from django.apps import AppConfig as DjangoAppConfig
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

from edc_protocol.cap import ALL_SITES
from edc_protocol.exceptions import SubjectTypeCapError

from .cap import Cap
from .subject_type import SubjectType

style = color_style()


class EdcProtocolConfigError(Exception):
    pass


class ArrowObject:

    def __init__(self, open_dt, close_dt):
        self.ropen = arrow.Arrow.fromdatetime(
            open_dt, open_dt.tzinfo).to('utc')
        self.rclose = arrow.Arrow.fromdatetime(
            close_dt, close_dt.tzinfo).to('utc')


class AppConfig(DjangoAppConfig):
    name = 'edc_protocol'
    verbose_name = 'Edc Protocol'

    # set with example defaults, you will need to change from your project
    protocol = 'BHP000'
    protocol_number = '000'  # 3 digits, used for identifiers
    protocol_name = 'My Protocol'
    protocol_title = 'My Protocol of Many Things'
    site_code = None
    site_name = None

    # these attributes are used by the SubjectTypeCapMixin
    subject_types = [
        SubjectType('subject', 'Research Subjects', Cap(
            model_name='edc_example.enrollment', max_subjects=9999)),
        SubjectType('subject', 'Research Subjects', Cap(
            model_name='edc_example.enrollmentthree', max_subjects=5))
    ]
    study_open_datetime = arrow.utcnow().floor('hour') - relativedelta(years=1)
    study_close_datetime = arrow.utcnow().ceil('hour')
    messages_written = False

    def ready(self):
        if not self.messages_written:
            sys.stdout.write(f'Loading {self.verbose_name} ...\n')
            sys.stdout.write(f' * {self.protocol}: {self.protocol_name}.\n')
            if not self.site_name:
                sys.stdout.write(style.ERROR(
                    ' ERROR. You need to define a site name! \n'))
            else:
                sys.stdout.write(f' * site_name: {self.site_name}.\n')
            if not self.site_code:
                sys.stdout.write(style.ERROR(
                    ' ERROR. You need to define a site code! \n'))
            else:
                sys.stdout.write(f' * site_code: {self.site_code}.\n')

        self.rstudy_open = arrow.Arrow.fromdatetime(
            self.study_open_datetime,
            self.study_open_datetime.tzinfo).to('utc').floor('hour')
        self.rstudy_close = arrow.Arrow.fromdatetime(
            self.study_close_datetime,
            self.study_close_datetime.tzinfo).to('utc').ceil('hour')

        self.study_open_datetime = self.rstudy_open.datetime
        self.study_close_datetime = self.rstudy_close.datetime

        open_date = self.study_open_datetime.strftime('%Y-%m-%d %Z')
        if not self.messages_written:
            sys.stdout.write(f' * Study opening date: {open_date}\n')
        close_date = self.study_close_datetime.strftime('%Y-%m-%d %Z')
        if not self.messages_written:
            sys.stdout.write(f' * Expected study closing date: {close_date}\n')
        if isinstance(self.subject_types, (list, tuple)):
            unique_labels = {}
            for subject_type in self.subject_types:
                for cap in subject_type.caps.values():
                    if cap.subject_type_name:
                        if cap.subject_type_name != subject_type.name:
                            raise SubjectTypeCapError(
                                'Subject type name does not match cap.')
                    else:
                        cap.subject_type_name = subject_type.name
                    label = f'{cap.subject_type_name}:{cap.model_name}:{cap.study_site}'
                    if label in unique_labels:
                        raise ImproperlyConfigured(
                            f'Enrollment cap not unique. Got {label}')
                    else:
                        unique_labels.update({label: cap})
            self.subject_types = {}
            for label, cap in unique_labels.items():
                self.subject_types.update({label: cap})
        if not self.messages_written:
            sys.stdout.write(' * Enrollment caps:\n')
            if len(self.subject_types) == 0:
                sys.stdout.write('   * None specified!\n')
            else:
                for label, cap in self.subject_types.items():
                    sys.stdout.write(f'   - found {cap}.\n')
            sys.stdout.write(f' Done loading {self.verbose_name}.\n')
        sys.stdout.flush()
        self.messages_written = True

    def get_cap(self, subject_type_name=None, model_name=None, study_site=None):
        try:
            cap = self.caps[f'{subject_type_name}:{model_name}:{study_site}']
        except KeyError:
            try:
                cap = self.caps[f'{subject_type_name}:{model_name}:{ALL_SITES}']
            except KeyError as e:
                raise SubjectTypeCapError(
                    f'Invalid criteria for Cap. Got {e}.')
        return cap

    @property
    def caps(self):
        return {cap.name: cap for cap in self.subject_types.values()}

    @property
    def arrow(self):
        return ArrowObject(self.study_open_datetime, self.study_close_datetime)
