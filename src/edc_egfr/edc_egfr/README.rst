|pypi| |actions| |codecov| |downloads|

edc-egfr
--------
Classes and utils to handle eGFR collection and reporting

Includes calculators for `CKD-EPI Creatinine equation (2009)`
and `Cockcroft-Gault`.

Calculate value, grade, percent drop, percent drop grade
========================================================

The calculators use ``edc_reportable`` to reference DAIDS tox tables.

.. code-block:: python

    egfr1 = EgfrCkdEpi(
            gender=MALE,
            ethnicity=BLACK,
            creatinine_value=53.0,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )
    self.assertEqual(round(egfr1.value, 2), 156.43)

and the eGFR grade

.. code-block:: python

    self.assertEqual(egfr1.egfr_grade, 0)


Percent drop from baseline
==========================
In a trial, we are interested in the eGFR percent from baseline. Any reference value can be passed as the
baseline value.

If the baseline value is not provided, the percent drop = 0:

.. code-block:: python

    # see edc-reportable for `reference_range_collection_name`
    opts = dict(
        gender=MALE,
        age_in_years=25,
        ethnicity=BLACK,
        creatinine_value=10.15,
        creatinine_units=MILLIGRAMS_PER_DECILITER,
        report_datetime=get_utcnow(),
        reference_range_collection_name="my_reference_list",
        calculator_name="ckd-epi",
    )
    egfr = Egfr(**opts)
    self.assertEqual(egfr.egfr_drop_value, 0.0)

If a baseline value is provided, the percent drop is calculated:

.. code-block:: python

    egfr = Egfr(baseline_egfr_value=23.0, **opts)
    self.assertEqual(round(egfr.egfr_value, 2), 7.33)
    self.assertEqual(egfr.egfr_grade, 4)
    self.assertEqual(round(egfr.egfr_drop_value, 2), 68.15)
    self.assertEqual(egfr.egfr_drop_grade, 4)

Notify on percent drop
======================

We can notify when the drop is more than a given percent. ``eGFR`` uses a custom
model to be updated.

A `edc` lab result CRF is filled in, ``calling_crf``, that has the creatinine value and units.
The ``calling_crf`` has a ``subject_visit``, ``report_datetime``, ``assay_datetime``, ``creatinine_value``, and ``creatinine_units``.

.. code-block:: python

    egfr = Egfr(
        baseline_egfr_value=220.1,
        notify_on_percent_drop=20,
        calling_crf=crf,
        **opts,
    )
    self.assertEqual(round(egfr.egfr_drop_value, 2), 28.93)
    self.assertTrue(
        EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
    )

Connecting a custom drop notification model with edc-action-item
================================================================

.. code-block:: python

    from edc_crf.crf_with_action_model_mixin import CrfWithActionModelMixin
    from edc_egfr.constants import EGFR_DROP_NOTIFICATION_ACTION
    from edc_egfr.model_mixins import EgfrDropNotificationModelMixin
    from edc_model import models as edc_models


    class EgfrDropNotification(
        EgfrDropNotificationModelMixin,
        CrfWithActionModelMixin,
        edc_models.BaseUuidModel,
    ):

        action_name = EGFR_DROP_NOTIFICATION_ACTION

        tracking_identifier_prefix = "EG"

        class Meta(edc_models.BaseUuidModel.Meta):
            verbose_name = "eGFR Drop Notification"
            verbose_name_plural = "eGFR Drop Notifications"


Adding to an EDC model.save()
=============================

For example, from the BloodResultRft model in `meta-edc`_

.. code-block:: python

    class BloodResultsRft(
        CrfModelMixin,
        CreatinineModelMixin,
        EgfrModelMixin,
        EgfrDropModelMixin,
        CrfWithRequisitionModelMixin,
        BloodResultsModelMixin,
        edc_models.BaseUuidModel,
    ):
        lab_panel = rft_panel
        egfr_formula_name = "ckd-epi"

        class Meta(CrfWithActionModelMixin.Meta, edc_models.BaseUuidModel.Meta):
            verbose_name = "Blood Result: RFT"
            verbose_name_plural = "Blood Results: RFT"





.. |pypi| image:: https://img.shields.io/pypi/v/edc-egfr.svg
    :target: https://pypi.python.org/pypi/edc-egfr

.. |actions| image:: https://github.com/clinicedc/edc-egfr/workflows/build/badge.svg?branch=develop
  :target: https://github.com/clinicedc/edc-egfr/actions?query=workflow:build

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-egfr/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-egfr

.. |downloads| image:: https://pepy.tech/badge/edc-egfr
   :target: https://pepy.tech/project/edc-egfr

.. _meta-edc: https://github.com/meta-trial/meta-edc/blob/develop/meta_subject/models/blood_results/blood_results_rft.py
