import six

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

# from edc.audit.audit_trail import AuditTrail

from ..helpers import AppointmentHelper
from ..choices import APPT_STATUS
from ..constants import DONE

from .base_appointment import BaseAppointment


class Appointment(BaseAppointment):
    """Tracks appointments for a registered subject's visit.

        Only one edc_appointment per subject visit_definition+visit_instance.
        Attribute 'visit_instance' should be populated by the system.
    """

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None', will raise an exception."""
        # for tests
        if not exception_cls:
            exception_cls = ValidationError
        if not self.id:
            appt_datetime = self.get_best_datetime(self.appt_datetime, self.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = self.change_datetime(
                self.best_appt_datetime, self.appt_datetime, self.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_visit_instance(self, using=None, exception_cls=None):
        """Confirms a 0 instance edc_appointment exists before allowing
        a continuation appt and keep a sequence."""
        if not exception_cls:
            exception_cls = ValidationError
        if not isinstance(self.visit_instance, six.string_types):
            raise exception_cls('Expected \'visit_instance\' to be of type string')
        if self.visit_instance != '0':
            if not Appointment.objects.using(using).filter(
                    registered_subject=self.registered_subject,
                    visit_definition=self.visit_definition,
                    visit_instance='0').exclude(pk=self.pk).exists():
                raise exception_cls(
                    'Cannot create continuation edc_appointment for visit {}. '
                    'Cannot find the original edc_appointment (visit instance equal to 0).'.format(
                        self.visit_definition,))
            if int(self.visit_instance) - 1 != 0:
                if not Appointment.objects.using(using).filter(
                        registered_subject=self.registered_subject,
                        visit_definition=self.visit_definition,
                        visit_instance=str(int(self.visit_instance) - 1)).exists():
                    raise exception_cls(
                        'Cannot create continuation edc_appointment for visit {0}. '
                        'Expected next visit instance to be {1}. Got {2}'.format(
                            self.visit_definition,
                            str(int(self.visit_instance) - 1),
                            self.visit_instance))

    def check_window_period(self, exception_cls=None):
        """Is this used?"""
        if not exception_cls:
            exception_cls = ValidationError
        if self.id:
            self.visit_definition.verify_datetime(self.appt_datetime, self.best_appt_datetime)

    def save(self, *args, **kwargs):
        """Django save method"""
        using = kwargs.get('using')
        if self.id:
            TimePointStatus = apps.get_model('data_manager', 'TimePointStatus')
            TimePointStatus.check_time_point_status(self, using=using)
        self.appt_datetime, self.best_appt_datetime = self.validate_appt_datetime()
        self.check_window_period()
        self.validate_visit_instance(using=using)
        AppointmentHelper().check_appt_status(self, using)
        super(Appointment, self).save(*args, **kwargs)

    def raw_save(self, *args, **kwargs):
        """Optional save to bypass stuff going on in the default save method."""
        super(Appointment, self).save(*args, **kwargs)

    def __str__(self):
        """Django."""
        return "{0} {1} for {2}.{3}".format(
            self.registered_subject.subject_identifier,
            self.registered_subject.subject_type,
            self.visit_definition.code,
            self.visit_instance)

    def dashboard(self):
        """Returns a hyperink for the Admin page."""
        ret = None
        if self.appt_status == APPT_STATUS[0][0]:
            return 'NEW'
        else:
            if self.registered_subject:
                if self.registered_subject.subject_identifier:
                    url = reverse(
                        'subject_dashboard_url',
                        kwargs={
                            'dashboard_type': self.registered_subject.subject_type.lower(),
                            'dashboard_model': 'edc_appointment',
                            'dashboard_id': self.pk,
                            'show': 'appointments'})
                    ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        return ret
    dashboard.allow_tags = True

    def get_subject_identifier(self):
        """Returns the subject identifier."""
        return self.registered_subject.subject_identifier

    def get_registered_subject(self):
        """Returns the registered subject."""
        return self.registered_subject

    def get_report_datetime(self):
        """Returns the edc_appointment datetime as the report_datetime."""
        return self.appt_datetime

    @property
    def complete(self):
        """Returns True if the edc_appointment status is DONE."""
        return self.appt_status == DONE

    def dispatch_container_lookup(self):
        return (self.__class__, 'id')

    def is_dispatched(self):
        """Returns the dispatched status based on the visit tracking
        form's id_dispatched response."""
        Visit = self.visit_definition.visit_tracking_content_type_map.model_class()
        return Visit.objects.get(appointment=self).is_dispatched()

    def include_for_dispatch(self):
        return True

    class Meta:
        """Django model Meta."""
        app_label = 'edc_appointment'
        db_table = 'bhp_appointment_appointment'
        unique_together = (('registered_subject', 'visit_definition', 'visit_instance'),)
        ordering = ['registered_subject', 'appt_datetime', ]
