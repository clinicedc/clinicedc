edc-timepoint
=============

Lock a "timepoint" from further editing once data is cleaned and reviewed.

With module ``edc_timepoint`` a data manager or supervisor is able to flag a model instance, that represents a timepoint, as closed to further edit. A good candidate for a "timepoint" model is one that is used to cover other data collection, such as an `edc_appointment.Appointment`. When the appointment status is set to something like 'complete' the timepoint status is set to ``closed`` and no further edits are allowed for data covered by that appointment.

Note: Check the tests to better understand how to configure this. Note that you will need to declare a custom ``SubjectVisit`` class and update settings.SUBJECT_VISIT_MODEL to point to the custom class.


Configuring the Timepoint Model
-------------------------------

Select a model that represent a timepoint. The model should at least have a `datetime` field and a `status` field. For example `Appointment`:


.. code-block:: python

    class Appointment(TimepointModelMixin, BaseUuidModel):

        appt_datetime = models.DateTimeField(
            verbose_name='Appointment date and time')

        appt_status = models.CharField(
            verbose_name='Status',
            choices=APPT_STATUS,
            max_length=25,
            default='NEW')

The ``TimepointModelMixin`` adds fields and methods prefixed as ``timepoint_<something>``. There is also a signal that is loaded in the ``AppConfig.ready`` that resets the timepoint attributes should ``Appointment.appt_status`` change from ``DONE``.

Only field ``timepoint_status`` is meant to be edited by the user. The other ``timepoint_<something>`` are managed automatically.

The user updates the ``Appointment`` normally closing it when the appointment is done. Then a data manager or supervisor can close the ``Appointment`` to further edit once the data has been reviewed.

To close the ``Appointment`` to further edit the code needs to call the ``timepoint_close_timepoint`` method:

.. code-block:: python

    appointment = Appointment.objects.create(**options)
    appointment.appt_status = 'DONE'
    appointment.timepoint_close_timepoint()

If the ``appointment.appt_status`` is not ``DONE`` when ``timepoint_close_timepoint`` is called, a ``TimepointError`` is raised.

If the appointment is successfully closed to further edit, any attempts to call ``appointment.save()`` will raise a ``TimepointError``.

The ``Appointment`` may be re-opened for edit by calling method ``timepoint_open_timepoint``.

Configuring others to use the Timepoint Model
---------------------------------------------

Continuing with the example above where ``Appointment`` is the timepoint model.

To prevent further edits to models related to ``Appointment``, configure the model with the ``TimepointLookupModelMixin`` and the ``TimepointLookup`` class. These models will refer to the timepoint model on ``save``.

For example:

.. code-block:: python

    class VisitTimepointLookup(TimepointLookup):
        timepoint_related_model_lookup = 'appointment'

    class VisitModel(TimepointLookupModelMixin, BaseUuidModel):

        timepoint_lookup_cls = VisitTimepointLookup

        appointment = models.ForeignKey(Appointment)

        report_datetime = models.DateTimeField(
            default=timezone.now)

If the timepoint model's ``timepoint_status`` is ``closed``, any attempt to create or modify ``VisitModel`` will raise a ``TimepointClosed`` exception.
