edc-visit-schedule
==================

Add longitudinal data collection schedules to your EDC project.


Installation
------------

Add to settings:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'edc_visit_schedule.apps.AppConfig',
        # ...
    ]

Overview
--------

* A ``Visit Schedule`` lives in your app in ``visit_schedules.py``. Each app can declare and register one or more visit schedules in its ``visit_schedules`` module. Visit schedules are loaded when ``autodiscover`` is called from ``AppConfig``.
* A ``VisitSchedule`` contains ``Schedules`` which contain ``Visits`` which contain ``Crfs`` and ``Requisitions``.
* A ``schedule`` is effectively a "data collection schedule" where each contained ``visit`` represents a data collection timepoint.
* A subject is put on a ``schedule`` by the schedule's ``onschedule`` model and taken off by the schedule's ``offschedule`` model. In the example below we use models ``OnSchedule`` and ``OffSchedule`` to do this for schedule ``schedule1``.

Usage
-----

First, create a file ``visit_schedules.py`` in the root of your app where the visit schedule code below will live.


Next, declare lists of data ``Crfs`` and laboratory ``Requisitions`` to be completed during each visit. For simplicity, we assume that every visit has the same data collection requirement (not usually the case).

.. code-block:: python

    from myapp.models import SubjectVisit, OnSchedule, OffSchedule, SubjectDeathReport, SubjectOffstudy

    from edc_visit_schedule.site_visit_schedules import site_visit_schedules
    from edc_visit_schedule.schedule import Schedule
    from edc_visit_schedule.visit import Crf, Requisition, CrfCollection, RequisitionCollection
    from edc_visit_schedule.visit_schedule import VisitSchedule


    crfs = CrfCollection(
        Crf(show_order=10, model='myapp.crfone'),
        Crf(show_order=20, model='myapp.crftwo'),
        Crf(show_order=30, model='myapp.crfthree'),
        Crf(show_order=40, model='myapp.crffour'),
        Crf(show_order=50, model='myapp.crffive'),
    )

    requisitions = RequisitionCollection(
        Requisition(
            show_order=10, model='myapp.subjectrequisition', panel_name='Research Blood Draw'),
        Requisition(
            show_order=20, model='myapp.subjectrequisition', panel_name='Viral Load'),
    )

Create a new visit schedule:

.. code-block:: python

    visit_schedule = VisitSchedule(
        name='visit_schedule',
        verbose_name='My Visit Schedule',
        death_report_model=SubjectDeathReport,
        offstudy_model=SubjectOffstudy)


Visit schedules contain ``Schedules`` so create a schedule:

.. code-block:: python

    schedule = Schedule(
        name='schedule',
        onschedule_model='myapp.onschedule',
        offschedule_model='myapp.offschedule',
        consent_definitions=[consent_definition_v1])

About consent_definitions:
    As you will see below, the ``schedule`` is a container for a data collection schedule of forms (CRFs and requisitions)
    for a single study timepoint or ``visit``. Ethically, a subject's data may not be collected before the subject has signed and submitted the informed consent form (ICF).
    ``Schedule`` is configured with information about the ICF that covers the forms it contains. When a form for a subject is validated and submitted, the ``Schedule`` will
    provide the consent_definition (or definitions) so that the calling object can confirm the subject is consented. The ICF is represented by
    the class ``ConsentDefinition`` from ``edc_consent``.

    See also class ``ConsentDefinition`` in ``edc_consent``.

Schedules contains visits, so declare some visits and add to the ``schedule``:

.. code-block:: python

    visit0 = Visit(
        code='1000',
        title='Visit 1000',
        timepoint=0,
        rbase=relativedelta(days=0),
        requisitions=requisitions,
        crfs=crfs)

    visit1 = Visit(
        code='2000',
        title='Visit 2000',
        timepoint=1,
        rbase=relativedelta(days=28),
        requisitions=requisitions,
        crfs=crfs)

    schedule.add_visit(visit=visit0)
    schedule.add_visit(visit=visit1)


Add the schedule to your visit schedule:

.. code-block:: python

    schedule = visit_schedule.add_schedule(schedule)

Register the visit schedule with the site registry:

.. code-block:: python

    visit_schedules.register(visit_schedule)

When Django loads, the visit schedule class will be available in the global ``site_visit_schedules``.

The ``site_visit_schedules`` has a number of methods to help query the visit schedule and some related data.

 **Note:** The ``schedule`` above was declared with ``onschedule_model=OnSchedule``. An on-schedule model uses the ``CreateAppointmentsMixin`` from ``edc_appointment``. On ``onschedule.save()`` the method ``onschedule.create_appointments`` is called. This method uses the visit schedule information to create the appointments as per the visit data in the schedule. See also ``edc_appointment``.

OnSchedule and OffSchedule models
---------------------------------

Two models mixins are required for the on-schedule and off-schedule models, ``OnScheduleModelMixin`` and ``OffScheduleModelMixin``. OnSchedule/OffSchedule models are specific to a ``schedule``. The ``visit_schedule_name`` and ``schedule_name`` are declared on the model's ``Meta`` class attribute ``visit_schedule_name``.

For example:

.. code-block:: python

    class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

        """A model used by the system. Auto-completed by subject_consent."""

        objects = SubjectIdentifierManager()

        on_site = CurrentSiteManager()

        history = HistoricalRecords()

        class Meta(OnScheduleModelMixin.Meta, BaseUuidModel.Meta):
            pass


    class OffSchedule(ActionModelMixin, OffScheduleModelMixin, BaseUuidModel):

        action_name = OFFSCHEDULE_ACTION

        class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Off-schedule"
            verbose_name_plural = "Off-schedule"
