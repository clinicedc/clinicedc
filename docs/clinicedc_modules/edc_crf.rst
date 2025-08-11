edc_crf
=======

In longitudinal clinical trials, CRFs (case report forms) are the most common
data collection forms required in the data collection schedule.

In addition to the logic checks that you will add for a specfic CRF, you also need
to validate a few general conditions. Most of these conditions are checked
relative to the ``report_datetime`` of the CRF data being submitted. Some examples
are:

* that a participant is consented and that their consent is still valid on the ``report_datetime``;
* that the CRF ``report_datetime`` makes sense relative to the covering visit report ``report_datetime``;
* that the participant is enrolled to the schedule (onschedule) on or after the ``report_datetime`` and has not been taken off the schedule (offschedule) on or before the ``report_datetime``;
* that the participant has not been taken off study on or before the ``report_datetime``.

CRF forms
+++++++++

The ``CrfModelFormMixin`` is used for all CRF modelforms. With this single
mixin the form:

* Checks for the consent relative to report datetime and this schedule (edc_consent);
* checks if participant is on/off schedule relative to report datetime and this schedule (edc_visit_schedule);
* validates subject_visit report datetime (edc_visit_tracking);
* checks if participant is offstudy relative to report datetime (edc_offstudy).

If any of the above conditions fail, a ``forms.ValidationError`` is raised.

The mixin imports mixins functionality from edc_consent_, edc_visit_schedule_,
edc_visit_tracking_, and edc_offstudy_.

.. code-block:: python

    from django import forms
    from edc_crf.modelform_mixins import CrfModelFormMixin
    from edc_form_validators import FormValidator

    from ..models import FollowupVitals


    class MyCrfFormValidator(FormValidator):
        pass


    class MyCrfForm(CrfModelFormMixin, forms.ModelForm):

        form_validator_cls = MyCrfFormValidator

        class Meta:
            model = MyCrf
            fields = "__all__"


CRF models
++++++++++

Similar to the ``CrfModelFormMixin``, the ``CrfModelMixin`` is used for all CRF models
and checks for the same conditions. However, if any of the conditions is met, an exception
is raised. You should render CRF models with a modelform class using the ``CRFModelFormMixin``
to catch these exceptions on the form where the user can respond.

.. code-block:: python

    class MyCrf(CrfModelMixin, BaseUuidModel):

        weight_determination = models.CharField(
            verbose_name="Is weight estimated or measured?",
            max_length=15,
            choices=WEIGHT_DETERMINATION,
        )

        class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "My CRF"
            verbose_name_plural = "My CRFs"


.. _edc_consent: https://github.com/clinicedc/clinicedc/tree/develop/src/edc-consent
.. _edc_visit_schedule: https://github.com/clinicedc/clinicedc/tree/develop/src/edc-visit-schedule
.. _edc_visit_tracking: https://github.com/clinicedc/clinicedc/tree/develop/src/edc-visit-tracking
.. _edc_offstudy: https://github.com/clinicedc/clinicedc/tree/develop/src/edc-offstudy
