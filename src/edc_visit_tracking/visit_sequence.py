from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class VisitSequenceError(Exception):
    pass


class VisitSequence:

    """A class that calculates the previous_visit and can enforce
    that visits are filled in sequence.
    """

    def __init__(self, appointment=None):
        self.appointment = appointment
        self.appointment_model_cls = self.appointment.__class__
        self.model_cls = getattr(
            self.appointment_model_cls,
            self.appointment_model_cls.related_visit_model_attr(),
        ).related.related_model
        self.subject_identifier = self.appointment.subject_identifier
        self.visit_schedule_name = self.appointment.visit_schedule_name
        self.visit_code = self.appointment.visit_code
        self.visit_code_sequence = self.appointment.visit_code_sequence

    def enforce_sequence(self):
        """Raises an exception if sequence is not adhered to; that is,
        the visits are not completed in order.
        """
        try:
            self.previous_visit
        except ObjectDoesNotExist:
            previous_visit_code_sequence = (
                0 if not self.visit_code_sequence else self.visit_code_sequence - 1
            )
            raise VisitSequenceError(
                "Previous visit report required. Enter report for "
                f"'{self.previous_visit_code}.{previous_visit_code_sequence}' "
                f"before completing this report."
            )

    @property
    def previous_visit_code(self):
        """Return the previous visit code or the existing
        visit code if sequence is not 0.
        """
        previous_visit_code = None
        if self.visit_code_sequence != 0:
            previous_visit_code = self.visit_code
        else:
            previous = self.appointment.schedule.visits.previous(self.visit_code)
            try:
                previous_visit_code = previous.code
            except AttributeError:
                pass
        return previous_visit_code

    @property
    def previous_appointment(self):
        """Returns the previous appointment model instance ir None.

        Considers visit code sequence.

        Raises `VisitSequenceError` if the expected sequence of
        appointments is broken. Expected sequence is based on
        the visit schedule.

        """
        # TODO: consider recreating missing appointments if sequence
        #       is broken

        opts = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=self.previous_visit_code,
        )
        try:
            previous_appointment = self.appointment_model_cls.objects.get(**opts)
        except ObjectDoesNotExist as e:
            if self.previous_visit_code:
                raise VisitSequenceError(
                    f"Appointment unexpectedly does not exist. Expected "
                    f"appointment {self.previous_visit_code}. "
                    f"Got {e}"
                )
            previous_appointment = None
        except MultipleObjectsReturned:
            if self.visit_code_sequence:
                opts.update(visit_code_sequence=self.visit_code_sequence - 1)
                try:
                    previous_appointment = self.appointment_model_cls.objects.get(
                        **opts
                    )
                except ObjectDoesNotExist:
                    raise VisitSequenceError(
                        f"Appointment unexpectedly does not exist. Expected "
                        f"appointment for {self.previous_visit_code}."
                        f"{self.visit_code_sequence - 1}."
                    )
            else:
                opts.update(visit_code_sequence__gte=self.visit_code_sequence)
                previous_appointment = (
                    self.appointment_model_cls.objects.filter(**opts)
                    .order_by("visit_code_sequence")
                    .last()
                )
        else:
            if previous_appointment.visit_code_sequence != 0:
                raise VisitSequenceError(
                    f"Missing appointment {self.previous_visit_code}.0. "
                    f"Unexpectedly got non-zero sequence for first appointment. "
                    f"See {previous_appointment}."
                )
        return previous_appointment

    @property
    def previous_visit(self):
        """Returns the previous visit model instance if it exists.
        """
        if self.previous_appointment:
            return self.model_cls.objects.get(appointment=self.previous_appointment)
        return None
