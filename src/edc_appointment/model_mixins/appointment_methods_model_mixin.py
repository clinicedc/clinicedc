from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_visit_tracking.model_mixins import VisitModelMixin


class AppointmentMethodsModelError(Exception):
    pass


class AppointmentMethodsModelMixin(models.Model):

    """Mixin of methods for the appointment model only.
    """

    @property
    def visit(self):
        """Returns the related visit model instance.
        """
        return getattr(self, self.related_visit_model_attr())

    @classmethod
    def related_visit_model_attr(cls):
        related_visit_model_attr = None
        fields = []
        for f in cls._meta.get_fields():
            if f.related_model:
                if issubclass(f.related_model, VisitModelMixin):
                    fields.append(f)
        if len(fields) > 1:
            raise AppointmentMethodsModelError(
                f"More than field on Appointment is related field to a visit model. "
                f"Got {fields}."
            )
        else:
            related_visit_model_attr = fields[0].name
        return related_visit_model_attr

    @classmethod
    def visit_model_cls(cls):
        return getattr(cls, cls.related_visit_model_attr()).related.related_model

    @property
    def next_by_timepoint(self):
        """Returns the next appointment or None of all appointments
        for this subject for visit_code_sequence=0.
        """
        return (
            self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                timepoint__gt=self.timepoint,
                visit_code_sequence=0,
            )
            .order_by("timepoint")
            .first()
        )

    @property
    def last_visit_code_sequence(self):
        """Returns an integer, or None, that is the visit_code_sequence
        of the last appointment for this visit code that is not self.
        (ordered by visit_code_sequence).

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        obj = (
            self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                visit_code=self.visit_code,
                visit_code_sequence__gt=self.visit_code_sequence,
            )
            .order_by("visit_code_sequence")
            .last()
        )
        if obj:
            return obj.visit_code_sequence
        return None

    @property
    def next_visit_code_sequence(self):
        """Returns an integer that is the next visit_code_sequence.

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        if self.last_visit_code_sequence:
            return self.last_visit_code_sequence + 1
        return self.visit_code_sequence + 1

    def get_last_appointment_with_visit_report(self):
        """Returns the last appointment model instance,
        or None, with a completed visit report.

        Ordering is by appointment timepoint/visit_code_sequence
        with a completed visit report.
        """
        appointment = None
        visit = (
            self.__class__.visit_model_cls()
            .objects.filter(
                appointment__subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
            )
            .order_by("appointment__timepoint", "appointment__visit_code_sequence")
            .last()
        )
        if visit:
            appointment = visit.appointment
        return appointment

    @property
    def previous_by_timepoint(self):
        """Returns the previous appointment or None by timepoint
        for visit_code_sequence=0.
        """
        return (
            self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                timepoint__lt=self.timepoint,
                visit_code_sequence=0,
            )
            .order_by("timepoint")
            .last()
        )

    @property
    def previous(self):
        """Returns the previous appointment or None in this schedule
        for visit_code_sequence=0.
        """
        return self.get_previous()

    def get_previous(self, include_interim=None):
        """Returns the previous appointment model instance,
        or None, in this schedule.

        Keywords:
            * include_interim: include interim appointments
              (e.g. those where visit_code_sequence != 0)
        """
        opts = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            timepoint__lt=self.timepoint,
        )
        if include_interim and self.visit_code_sequence != 0:
            opts.pop("timepoint__lt")
            opts.update(timepoint__lte=self.timepoint)
        elif not include_interim:
            opts.update(visit_code_sequence=0)
        appointments = (
            self.__class__.objects.filter(**opts)
            .exclude(id=self.id)
            .order_by("timepoint", "visit_code_sequence")
        )
        try:
            previous_appt = appointments.reverse()[0]
        except IndexError:
            previous_appt = None
        return previous_appt

    @property
    def next(self):
        """Returns the next appointment or None in this schedule
        for visit_code_sequence=0.
        """
        next_appt = None
        next_visit = self.schedule.visits.next(self.visit_code)
        if next_visit:
            try:
                options = dict(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    visit_code=next_visit.code,
                    visit_code_sequence=0,
                )
                next_appt = self.__class__.objects.get(**options)
            except ObjectDoesNotExist:
                pass
        return next_appt

    class Meta:
        abstract = True
