edc-appointment
---------------

This module works closely with ``edc_visit_tracking`` and ``edc_visit_schedule``.

Subject data is collected on predefined timepoints. We describe these data collection timepoints in a ``visit_schedule`` as provided by ``edc-visit-schedule``. In ``edc-appointment`` timepoints are represented by appointments. ``edc-appointment`` provides classes for creating and managing appointments.

See also ``edc-visit-schedule``.


AppointmentModelMixin
+++++++++++++++++++++

A model mixin for the Appointment model. Each project may have one appointment model. For example:

.. code-block:: python

    class Appointment(AppointmentModelMixin, RequiresConsentModelMixin, BaseUuidModel):

        class Meta(AppointmentModelMixin.Meta):
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'


Appointment is a required foreignkey for the visit report
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The ``Appointment`` model is a required foreignkey for the visit report. Be sure to set ``on_delete=PROTECT``.

.. code-block:: python

    class SubjectVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin,
                       RequiresConsentModelMixin, BaseUuidModel):

        appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

        objects = VisitModelManager()

        class Meta(VisitModelMixin.Meta):
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'


CreatesAppointmentsModelMixin
+++++++++++++++++++++++++++++

A model mixin for the model that triggers the creation of appointments when the model is saved. This is typically an enrollment model.

Adds the model field ``facility``. The value of field ``facility`` tells the ``CreateAppointmentsMixin`` to create appointments for the subject on dates that are available at the ``facility``.

.. code-block:: python

    class Enrollment(EnrollmentModelMixin, CreateAppointmentsMixin,
                     RequiresConsentModelMixin, BaseUuidModel):

        class Meta(EnrollmentModelMixin.Meta):
            visit_schedule_name = 'subject_visit_schedule.schedule1'
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'

When ``Enrollment`` declared above is saved, one appointment will be created for the subject for each ``visit`` in schedule ``schedule1`` of visit_schedule ``subject_visit_schedule``.

Note: the value for ``facility`` must be provided by the user, either through the form interface or programmatically.


Customizing appointment scheduling by ``Facility``
++++++++++++++++++++++++++++++++++++++++++++++++++

see ``edc_facility``


Available Appointment Model Manager Methods
===========================================

The ``Appointment`` model is declared with ``AppointmentManager``. It has several useful methods.


first_appointment() last_appointment()
++++++++++++++++++++++++++++++++++++++

Returns the first (or last) appointment. If just the ``subject_identifier`` is provided, the first appointment of the protocol for the subject is returned. To be more specific, provide ``{subject_identifier=subject_identifier, visit_schedule_name=visit_schedule_name}``.
To be even more specific,  ``{subject_identifier=subject_identifier, visit_schedule_name=visit_schedule_name, schedule_name=schedule_name}``.

The most common usage is to just provide these values with an appointment instance:

.. code-block:: python

    first_appointment = Appointment.objects.first_appointment(appointment=appointment)


next_appointment() previous_appointment()
+++++++++++++++++++++++++++++++++++++++++

The next and previous appointment are relative to the schedule and a visit_code within that schedule. If next is called on the last appointment in the sequence ``None`` is returned. If previous is called on the first appointment in the sequence ``None`` is returned.

For example, in a sequence of appointment 1000, 2000, 3000, 4000:

.. code-block:: python

    >>> appointment.visit_code
    1000
    >>> next_appointment = Appointment.objects.next_appointment(appointment=appointment)
    >>> next_appointment.visit_code
    2000


But you can also pass an appointment instance and pass the visit code:

.. code-block:: python

    >>> appointment.visit_code
    1000
    >>> next_appointment = Appointment.objects.next_appointment(
            appointment=appointment, visit_code=3000)
    >>> next_appointment.visit_code
    4000


If you ask for the next appointment from the last, ``None`` is returned:

.. code-block:: python

    >>> appointment.visit_code
    4000
    >>> next_appointment = Appointment.objects.next_appointment(
            appointment=appointment, visit_code=3000)
    >>> next_appointment.visit_code
    AttributeError: 'NoneType' object has no attribute 'visit_code'


The ``previous_appointment`` acts as expected:

.. code-block:: python

    >>> appointment.visit_code
    1000
    >>> previous_appointment = Appointment.objects.previous_appointment(appointment=appointment)
    >>> previous_appointment.visit_code
    AttributeError: 'NoneType' object has no attribute 'visit_code'


delete_for_subject_after_date()
+++++++++++++++++++++++++++++++

This method will delete all appointments for a subject after a given datetime. See also ``edc-offstudy``.

``Appointment`` is usually a foreignkey of a visit model. It's important when using this method to ensure that when declaring ``Appointment`` as a foreignkey you explicitly set ``on_delete=PROTECT``. If you don't, the deletion will cascade to other related instances -- and that's bad.

.. code-block:: python

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

Allowing appointments to be skipped using SKIPPED_APPT
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Set ``settings.EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING`` to a list of tuples .. [(lower_label, field_name), ...]. The default is ``[]``::

    EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING = [("edc_appointment_app.nextappointment", "appt_date")]

When set, options to skip the appointment will be available on the Appointment form.

Note:
    This option does not make sense for longitudinal trials following a protocol defined schedule. However
    if part of the follow up is driven by routine care, for example, where patients do not follow a strict
    schedule, then it may be useful.

Using a CRF to record the next appointment date
+++++++++++++++++++++++++++++++++++++++++++++++

For routine care, the next appointment date is not set by the protocol. The EDC will create appointments
according to the visit schedule as usual, but the dates will be approximate. You can administer a CRF at the
end of each visit to capture the next appointment date. A signal will update the appointment
that best matches the date given. Use this together with SKIPPED_APPT (see above).

Set ``settings.EDC_APPOINTMENT_MAX_MONTHS_TO_NEXT_APPT`` to a limit the number of months ahead for next appointment date::

    EDC_APPOINTMENT_MAX_MONTHS_TO_NEXT_APPT = 6 # default

.. code-block:: python

    # model.py
    class NextAppointmentCrf(NextAppointmentCrfModelMixin, CrfModelMixin, BaseUuidModel):

        class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Next Appointment"
            verbose_name_plural = "Next Appointments"


    # forms.py
    class NextAppointmentCrfForm(NextAppointmentCrfModelFormMixin, CrfModelFormMixin, forms.ModelForm):
        form_validator_cls = NextAppointmentCrfFormValidator

        class Meta:
            model = NextAppointmentCrf
            fields = "__all__"


    # admin.py
    @admin.register(NextAppointmentCrf, site=intecomm_subject_admin)
    class NextAppointmentCrfAdmin(NextAppointmenCrftModelAdminMixin, CrfModelAdmin):
        form = NextAppointmentCrfForm

