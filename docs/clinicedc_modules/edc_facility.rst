edc-facility
============

Loading holidays
----------------

To load the list of holidays into the system:

.. code-block:: bash

    python manage.py import_holidays


Customizing appointment scheduling by ``Facility``
--------------------------------------------------

Appointment scheduling can be customized per ``facility`` or clinic:

Add each facility to ``app_config.facilities`` specifying the facility ``name``, ``days`` open and the maximum number of ``slots`` available per day:

.. code-block:: python

    from edc_facility.apps import AppConfig as EdcAppointmentAppConfig

    class AppConfig(EdcAppointmentAppConfig):

        facilities = {
            'clinic1': Facility(name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]),
            'clinic2': Facility(name='clinic', days=[MO, WE, FR], slots=[30, 30, 30])
        }

To schedule an appointment that falls on a day that the clinic is open, isn't a holiday and isn't already over-booked:

.. code-block:: python

    from edc_utils import get_utcnow
    from .facility import Facility

    suggested_datetime = get_utcnow()
    available_datetime = facility.available_datetime(suggested_datetime)


If holidays are entered (in model ``Holiday``) and the appointment lands on a holiday, the appointment date is incremented forward to an allowed weekday. Assuming ``facility`` is configured in ``app_config`` to only schedule appointments on [TU, TH]:

.. code-block:: python

    from datetime import datetime
    from dateutil.relativedelta import TU, TH
    from django.conf import settings
    from django.utils import timezone
    from zoneifo import ZoneInfo

    from .facility import Facility
    from .models import Holiday

    Holiday.objects.create(
        name='Id-ul-Adha (Feast of the Sacrifice)',
        date=date(2015, 9, 24)
    )
    suggested_datetime = datetime(2015, 9, 24, tzinfo=ZoneInfo("UTC"))  # TH
    available_datetime = facility.available_datetime(suggested_datetime)
    print(available_datetime)  # 2015-09-29 00:00:00, TU

The maximum number of possible scheduling slots per day is configured in ``app_config``. As with the holiday example above, the appointment date will be incremented forward to a day with an available slot.


System checks
-------------
* ``edc_facility.001`` Holiday file not set! settings.HOLIDAY_FILE not defined.
* ``edc_facility.002`` Holiday file not found.
* ``edc_facility.003`` Holiday table is empty. Run management command 'import_holidays'.
* ``edc_facility.004`` No Holidays have been defined for this country.


HealthFacility model
--------------------

The ``HealthFacility`` model is used by ``edc-next-appointment`` when reporting the next routine
appointment for a participant. This is important for trials that collect data at routine clinic appointments
not set by the research staff or defined by the protocol.

See also ``edc-next-appointment``.

If you need to customize the model, declare the concrete model locally in your app. You can use the mixins to build
your own classes.

You'll also need to update ``settings`` to tell ``edc_facility`` where the custom model is::

    EDC_FACILITY_HEALTH_FACILITY_MODEL = "myapp.healthfacility"


For example:

.. code-block:: python

    # models.py
    class HealthFacility(SiteModelMixin, HealthFacilityModelMixin, BaseUuidModel):

        objects = Manager()
        on_site = CurrentSiteManager()
        history = HistoricalRecords()

        class Meta(SiteModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Health Facility"
            verbose_name_plural = "Health Facilities"

.. code-block:: python

    # forms.py
    class HealthFacilityForm(FormValidatorMixin, forms.ModelForm):
        form_validator_cls = HealthFacilityFormValidator

        class Meta:
            model = HealthFacility
            fields = "__all__"

.. code-block:: python

    # admin.py
    @admin.register(HealthFacility, site=intecomm_facility_admin)
    class HealthFacilityAdmin(
        HealthFacilityModelAdminMixin,
        SiteModelAdminMixin,
        BaseModelAdminMixin,
    ):
        form = HealthFacilityForm
