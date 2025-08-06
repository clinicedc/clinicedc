
.. code-block:: text

    2025/08/06

    We are in the process of merging all edc modules into this one repo, so this is a work in progress.

    Stable version of edc is https://github.com/clinicedc/edc v1.2.7



|pypi| |downloads| |black| |django-packages|

clinicedc -  A clinical trials data management framework built on Django
========================================================================

A data management framework built on Django for multisite randomized longitudinal clinical trials.

`Here are a set of python modules that extend Django <https://github.com/clinicedc/edc>`__ to empower you to build an EDC / eSource system to handle data
collection and management for multi-site longitudinal clinical trials.

Refer to the specific open projects listed below for example EDC systems built with these modules.
The more recent the trial the better the example.

The codebase continues to evolve over many years of conducting clinical trials for mostly NIH-funded clinical trials through
the `Harvard T Chan School of Public Health <https://aids.harvard.edu>`__, the
`Botswana-Harvard AIDS Institute Partnership <https://aids.harvard.edu/research/bhp>`__
in Gaborone, Botswana and the `London School of Hygiene and Tropical Medicine <https://lshtm.ac.uk>`__.
Almost all trials were originally related to HIV/AIDS research.

More recent work with the `RESPOND Africa Group <https://www.ucl.ac.uk/global-health/respond-africa>`__ formerly at the
`Liverpool School of Tropical Medicine <https://lstm.ac.uk>`__ and now with the `University College London Institute for Global Health <https://www.ucl.ac.uk/global-health/>`__ has expanded into Diabetes (DM),
Hypertension (HTN) and models of integrating care in Africa (https://inteafrica.org) for the
three main chronic conditions -- HIV/DM/HTN.

See also https://www.ucl.ac.uk/global-health/respond-africa

The implementations we develop with this framework are mostly eSource systems rather than the traditional EDCs.

The ``clinicedc's`` listed below consist of a subset of trial-specific modules that make heavy use of modules in this framework.

(python 3.12+, Django 5.2+, MySQL 8+, see setup.cfg)


How we describe the EDC in our protocol documents
-------------------------------------------------

Here is a simple example of a data management section for a study protocol document: `data_management_section`_

.. _data_management_section: https://github.com/clinicedc/edc/blob/main/docs/protocol_data_management_section.rst


Projects that use ``clinicedc``
-------------------------------
Recent examples of ``clinicedc`` applications using this codebase:

INTECOMM
--------
Controlling chronic diseases in Africa: Development and evaluation of an integrated community-based management model for HIV, Diabetes and Hypertension in Tanzania and Uganda

https://github.com/intecomm-trial/intecomm-edc (2022- )

EFFECT
------
Fluconazole plus flucytosine vs. fluconazole alone for cryptococcal antigen-positive patients identified through screening:

A phase III randomised controlled trial

https://github.com/effect-trial/effect-edc (2021- )

http://www.isrctn.com/ISRCTN30579828

META Trial (Phase III)
~~~~~~~~~~~~~~~~~~~~~~
A randomised placebo-controlled double-blind phase III trial to determine the effects of metformin versus placebo on the incidence of diabetes in HIV-infected persons with pre-diabetes in Tanzania.

https://github.com/meta-trial/meta-edc (2021- )

(The same codebase is used for META Phase 2 and META Phase 3)

http://www.isrctn.com/ISRCTN77382043

Mapitio
~~~~~~~

Retrospective HIV/Diabetes/Hypertension Cohort (Tanzania)

https://github.com/mapitio/mapitio-edc (2020-2022)

MOCCA
~~~~~

Integrated care for HIV and non-communicable diseases in Africa: a pilot study to inform a large-scale trial (MOCCA and MOCCA Extension Study)

https://github.com/mocca-trail/mocca-edc (2020-2022)

http://www.isrctn.com/ISRCTN71437522

INTE Africa Trial
~~~~~~~~~~~~~~~~~
Evaluating the integration of health services for chronic diseases in Africa

(32 sites in Uganda and Tanzania)

https://github.com/inte-africa-trial/inte-edc (2020-2022)

https://inteafrica.org

http://www.isrctn.com/ISRCTN43896688

META Trial (Phase II)
~~~~~~~~~~~~~~~~~~~~~
A randomised placebo-controlled double-blind phase II trial to determine the effects of metformin versus placebo on the incidence of diabetes in HIV-infected persons with pre-diabetes in Tanzania.

(3 sites in Tanzania)

https://github.com/meta-trial/meta-edc (2019-2021)

http://www.isrctn.com/ISRCTN76157257


The Ambition Trial
~~~~~~~~~~~~~~~~~~

High dose AMBISOME on a fluconazole backbone for cryptococcal meningitis induction therapy in sub-Saharan Africa

(7 sites in Botswana, Malawi, South Africa, Uganda, Zimbabwe)

https://github.com/ambition-trial/ambition-edc (2018-2021)

http://www.isrctn.com/ISRCTN72509687

Start with main repo `ambition-edc`

The Botswana Combination Prevention Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(30 remote offline sites in Botswana)

https://github.com/botswana-combination-prevention-project (2013-2018)

https://clinicaltrials.gov/ct2/show/NCT01965470

https://www.ncbi.nlm.nih.gov/pubmed/?term=NCT01965470

https://aids.harvard.edu/tag/bcpp/

Start with main repo `bcpp`

Contacts
--------

For further information go to https://github.com/erikvw.

|django| |jet-brains|



=========================== ============================= ==================================
edc-csf_                    |edc-csf|                     |pypi-edc-csf|
edc-dx_                     |edc-dx|                      |pypi-edc-dx|
edc-dx-review_              |edc-dx-review|               |pypi-edc-dx-review|
edc-egfr_                   |edc-egfr|                    |pypi-edc-egfr|
edc-glucose_                |edc-glucose|                 |pypi-edc-glucose|
edc-he_                     |edc-he|                      |pypi-edc-he|
edc-microbiology_           |edc-microbiology|            |pypi-edc-microbiology|
edc-microscopy_             |edc-microscopy|              |pypi-edc-microscopy|
edc-mnsi_                   |edc-mnsi|                    |pypi-edc-mnsi|
edc-next-appointment_       |edc-next-appointment|        |pypi-edc-next-appointment|
edc-qol_                    |edc-qol|                     |pypi-edc-qol|
edc-vitals_                 |edc-vitals|                  |pypi-edc-vitals|
=========================== ============================= ==================================


Thanks to JetBrains for support with an opensource PyCharm IDE license. |jet-brains|


.. |pypi| image:: https://img.shields.io/pypi/v/clinicedc.svg
    :target: https://pypi.python.org/pypi/edc

.. |downloads| image:: https://pepy.tech/badge/clinicedc
   :target: https://pepy.tech/project/clinicedc

.. |django| image:: https://www.djangoproject.com/m/img/badges/djangomade124x25.gif
   :target: http://www.djangoproject.com/
   :alt: Made with Django


.. _edc-csf: https://github.com/clinicedc/edc-csf
.. _edc-dx: https://github.com/clinicedc/edc-dx
.. _edc-dx-review: https://github.com/clinicedc/edc-dx-review
.. _edc-egfr: https://github.com/clinicedc/edc-egfr
.. _edc-glucose: https://github.com/clinicedc/edc-glucose
.. _edc-he: https://github.com/clinicedc/edc-he
.. _edc-mnsi: https://github.com/clinicedc/edc-mnsi
.. _edc-microbiology: https://github.com/clinicedc/edc-microbiology
.. _edc-microscopy: https://github.com/clinicedc/edc-microscopy
.. _edc-next-appointment: https://github.com/clinicedc/edc-next-appointment
.. _edc-qol: https://github.com/clinicedc/edc-qol
.. _edc-test-utils: https://github.com/clinicedc/edc-test-utils
.. _edc-vitals: https://github.com/clinicedc/edc-vitals

.. |edc-action-item| image:: https://github.com/clinicedc/edc-action-item/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-action-item/actions/workflows/build.yml
.. |edc-adherence| image:: https://github.com/clinicedc/edc-adherence/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-adherence/actions/workflows/build.yml
.. |edc-adverse-event| image:: https://github.com/clinicedc/edc-adverse-event/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-adverse-event/actions/workflows/build.yml
.. |edc-appointment| image:: https://github.com/clinicedc/edc-appointment/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-appointment/actions/workflows/build.yml
.. |edc-appconfig| image:: https://github.com/clinicedc/edc-appconfig/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-appconfig/actions/workflows/build.yml
.. |edc-auth| image:: https://github.com/clinicedc/edc-auth/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-auth/actions/workflows/build.yml
.. |edc-clinic| image:: https://github.com/clinicedc/edc-clinic/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-clinic/actions/workflows/build.yml
.. |edc-consent| image:: https://github.com/clinicedc/edc-consent/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-consent/actions/workflows/build.yml
.. |edc-crf| image:: https://github.com/clinicedc/edc-crf/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-crf/actions/workflows/build.yml
.. |edc-csf| image:: https://github.com/clinicedc/edc-csf/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-csf/actions/workflows/build.yml
.. |edc-dashboard| image:: https://github.com/clinicedc/edc-dashboard/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-dashboard/actions/workflows/build.yml
.. |edc-data-manager| image:: https://github.com/clinicedc/edc-data-manager/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-data-manager/actions/workflows/build.yml
.. |edc-device| image:: https://github.com/clinicedc/edc-device/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-device/actions/workflows/build.yml
.. |edc-document-status| image:: https://github.com/clinicedc/edc-document-status/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-document-status/actions/workflows/build.yml
.. |edc-dx| image:: https://github.com/clinicedc/edc-dx/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-dx/actions/workflows/build.yml
.. |edc-dx-review| image:: https://github.com/clinicedc/edc-dx-review/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-dx-review/actions/workflows/build.yml
.. |edc-egfr| image:: https://github.com/clinicedc/edc-egfr/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-egfr/actions/workflows/build.yml
.. |edc-export| image:: https://github.com/clinicedc/edc-export/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-export/actions/workflows/build.yml
.. |edc-facility| image:: https://github.com/clinicedc/edc-facility/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-facility/actions/workflows/build.yml
.. |edc-fieldsets| image:: https://github.com/clinicedc/edc-fieldsets/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-fieldsets/actions/workflows/build.yml
.. |edc-form-describer| image:: https://github.com/clinicedc/edc-form-describer/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-form-describer/actions/workflows/build.yml
.. |edc-form-label| image:: https://github.com/clinicedc/edc-form-label/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-form-label/actions/workflows/build.yml
.. |edc-form-runners| image:: https://github.com/clinicedc/edc-form-runners/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-form-runners/actions/workflows/build.yml
.. |edc-form-validators| image:: https://github.com/clinicedc/edc-form-validators/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-form-validators/actions/workflows/build.yml
.. |edc-glucose| image:: https://github.com/clinicedc/edc-glucose/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-glucose/actions/workflows/build.yml
.. |edc-he| image:: https://github.com/clinicedc/edc-he/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-he/actions/workflows/build.yml
.. |edc-identifier| image:: https://github.com/clinicedc/edc-identifier/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-identifier/actions/workflows/build.yml
.. |edc-lab| image:: https://github.com/clinicedc/edc-lab/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-lab/actions/workflows/build.yml
.. |edc-lab-dashboard| image:: https://github.com/clinicedc/edc-lab-dashboard/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-lab-dashboard/actions/workflows/build.yml
.. |edc-lab-panel| image:: https://github.com/clinicedc/edc-lab-panel/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-lab-panel/actions/workflows/build.yml
.. |edc-lab-results| image:: https://github.com/clinicedc/edc-lab-results/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-lab-results/actions/workflows/build.yml
.. |edc-label| image:: https://github.com/clinicedc/edc-label/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-label/actions/workflows/build.yml
.. |edc-list-data| image:: https://github.com/clinicedc/edc-list-data/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-list-data/actions/workflows/build.yml
.. |edc-listboard| image:: https://github.com/clinicedc/edc-listboard/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-listboard/actions/workflows/build.yml
.. |edc-locator| image:: https://github.com/clinicedc/edc-locator/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-locator/actions/workflows/build.yml
.. |edc-ltfu| image:: https://github.com/clinicedc/edc-ltfu/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-ltfu/actions/workflows/build.yml
.. |edc-metadata| image:: https://github.com/clinicedc/edc-metadata/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-metadata/actions/workflows/build.yml
.. |edc-metadata-rules| image:: https://github.com/clinicedc/edc-metadata-rules/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-metadata-rules/actions/workflows/build.yml
.. |edc-mnsi| image:: https://github.com/clinicedc/edc-mnsi/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-mnsi/actions/workflows/build.yml
.. |edc-microbiology| image:: https://github.com/clinicedc/edc-microbiology/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-microbiology/actions/workflows/build.yml
.. |edc-microscopy| image:: https://github.com/clinicedc/edc-microscopy/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-microscopy/actions/workflows/build.yml
.. |edc-model| image:: https://github.com/clinicedc/edc-model/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-model/actions/workflows/build.yml
.. |edc-model-admin| image:: https://github.com/clinicedc/edc-model-admin/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-model-admin/actions/workflows/build.yml
.. |edc-model-fields| image:: https://github.com/clinicedc/edc-model-fields/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-model-fields/actions/workflows/build.yml
.. |edc-model-form| image:: https://github.com/clinicedc/edc-model-form/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-model-form/actions/workflows/build.yml
.. |edc-model-to-dataframe| image:: https://github.com/clinicedc/edc-model-to-dataframe/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-model-to-dataframe/actions/workflows/build.yml
.. |edc-navbar| image:: https://github.com/clinicedc/edc-navbar/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-navbar/actions/workflows/build.yml
.. |edc-next-appointment| image:: https://github.com/clinicedc/edc-next-appointment/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-next-appointment/actions/workflows/build.yml
.. |edc-notification| image:: https://github.com/clinicedc/edc-notification/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-notification/actions/workflows/build.yml
.. |edc-offstudy| image:: https://github.com/clinicedc/edc-offstudy/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-offstudy/actions/workflows/build.yml
.. |edc-pdutils| image:: https://github.com/clinicedc/edc-pdutils/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-pdutils/actions/workflows/build.yml
.. |edc-pharmacy| image:: https://github.com/clinicedc/edc-pharmacy/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-pharmacy/actions/workflows/build.yml
.. |edc-prn| image:: https://github.com/clinicedc/edc-prn/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-prn/actions/workflows/build.yml
.. |edc-protocol| image:: https://github.com/clinicedc/edc-protocol/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-protocol/actions/workflows/build.yml
.. |edc-protocol-incident| image:: https://github.com/clinicedc/edc-protocol-incident/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-protocol-incident/actions/workflows/build.yml
.. |edc-pylabels| image:: https://github.com/clinicedc/edc-pylabels/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-pylabels/actions/workflows/build.yml
.. |edc-randomization| image:: https://github.com/clinicedc/edc-randomization/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-randomization/actions/workflows/build.yml
.. |edc-refusal| image:: https://github.com/clinicedc/edc-refusal/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-refusal/actions/workflows/build.yml
.. |edc-registration| image:: https://github.com/clinicedc/edc-registration/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-registration/actions/workflows/build.yml
.. |edc-reportable| image:: https://github.com/clinicedc/edc-reportable/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-reportable/actions/workflows/build.yml
.. |edc-pdf-reports| image:: https://github.com/clinicedc/edc-pdf-reports/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-pdf-reports/actions/workflows/build.yml
.. |edc-qareports| image:: https://github.com/clinicedc/edc-qareports/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-qareports/actions/workflows/build.yml
.. |edc-qol| image:: https://github.com/clinicedc/edc-qol/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-qol/actions/workflows/build.yml
.. |edc-review-dashboard| image:: https://github.com/clinicedc/edc-review-dashboard/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-review-dashboard/actions/workflows/build.yml
.. |edc-rx| image:: https://github.com/clinicedc/edc-rx/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-rx/actions/workflows/build.yml
.. |edc-screening| image:: https://github.com/clinicedc/edc-screening/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-screening/actions/workflows/build.yml
.. |edc-search| image:: https://github.com/clinicedc/edc-search/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-search/actions/workflows/build.yml
.. |edc-sites| image:: https://github.com/clinicedc/edc-sites/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-sites/actions/workflows/build.yml
.. |edc-subject-dashboard| image:: https://github.com/clinicedc/edc-subject-dashboard/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-subject-dashboard/actions/workflows/build.yml
.. |edc-test-utils| image:: https://github.com/clinicedc/edc-test-utils/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-test-utils/actions/workflows/build.yml
.. |edc-timepoint| image:: https://github.com/clinicedc/edc-timepoint/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-timepoint/actions/workflows/build.yml
.. |edc-transfer| image:: https://github.com/clinicedc/edc-transfer/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-transfer/actions/workflows/build.yml
.. |edc-unblinding| image:: https://github.com/clinicedc/edc-unblinding/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-unblinding/actions/workflows/build.yml
.. |edc-utils| image:: https://github.com/clinicedc/edc-utils/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-utils/actions/workflows/build.yml
.. |edc-view-utils| image:: https://github.com/clinicedc/edc-view-utils/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-view-utils/actions/workflows/build.yml
.. |edc-visit-schedule| image:: https://github.com/clinicedc/edc-visit-schedule/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-visit-schedule/actions/workflows/build.yml
.. |edc-visit-tracking| image:: https://github.com/clinicedc/edc-visit-tracking/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-visit-tracking/actions/workflows/build.yml
.. |edc-vitals| image:: https://github.com/clinicedc/edc-vitals/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-vitals/actions/workflows/build.yml

.. |pypi-edc-action-item| image:: https://img.shields.io/pypi/v/edc-action-item.svg
    :target: https://pypi.python.org/pypi/edc-action-item
.. |pypi-edc-adherence| image:: https://img.shields.io/pypi/v/edc-adherence.svg
    :target: https://pypi.python.org/pypi/edc-adherence
.. |pypi-edc-adverse-event| image:: https://img.shields.io/pypi/v/edc-adverse-event.svg
    :target: https://pypi.python.org/pypi/edc-adverse-event
.. |pypi-edc-analytics| image:: https://img.shields.io/pypi/v/edc-analytics.svg
    :target: https://pypi.python.org/pypi/edc-analytics
.. |pypi-edc-appointment| image:: https://img.shields.io/pypi/v/edc-appointment.svg
    :target: https://pypi.python.org/pypi/edc-appointment
.. |pypi-edc-appconfig| image:: https://img.shields.io/pypi/v/edc-appconfig.svg
    :target: https://pypi.python.org/pypi/edc-appconfig
.. |pypi-edc-auth| image:: https://img.shields.io/pypi/v/edc-auth.svg
    :target: https://pypi.python.org/pypi/edc-auth
.. |pypi-edc-blood-results| image:: https://img.shields.io/pypi/v/edc-blood-results.svg
    :target: https://pypi.python.org/pypi/edc-blood-results
.. |pypi-edc-consent| image:: https://img.shields.io/pypi/v/edc-consent.svg
    :target: https://pypi.python.org/pypi/edc-consent
.. |pypi-edc-constants| image:: https://img.shields.io/pypi/v/edc-constants.svg
    :target: https://pypi.python.org/pypi/edc-constants
.. |pypi-edc-crf| image:: https://img.shields.io/pypi/v/edc-crf.svg
    :target: https://pypi.python.org/pypi/edc-crf
.. |pypi-edc-csf| image:: https://img.shields.io/pypi/v/edc-csf.svg
    :target: https://pypi.python.org/pypi/edc-csf
.. |pypi-edc-dashboard| image:: https://img.shields.io/pypi/v/edc-dashboard.svg
    :target: https://pypi.python.org/pypi/edc-dashboard
.. |pypi-edc-data-manager| image:: https://img.shields.io/pypi/v/edc-data-manager.svg
    :target: https://pypi.python.org/pypi/edc-data-manager
.. |pypi-edc-device| image:: https://img.shields.io/pypi/v/edc-device.svg
    :target: https://pypi.python.org/pypi/edc-device
.. |pypi-edc-document-status| image:: https://img.shields.io/pypi/v/edc-document-status.svg
    :target: https://pypi.python.org/pypi/edc-document-status
.. |pypi-edc-dx| image:: https://img.shields.io/pypi/v/edc-dx.svg
    :target: https://pypi.python.org/pypi/edc-dx
.. |pypi-edc-dx-review| image:: https://img.shields.io/pypi/v/edc-dx-review.svg
    :target: https://pypi.python.org/pypi/edc-dx-review
.. |pypi-edc-egfr| image:: https://img.shields.io/pypi/v/edc-egfr.svg
    :target: https://pypi.python.org/pypi/edc-egfr
.. |pypi-edc-export| image:: https://img.shields.io/pypi/v/edc-export.svg
    :target: https://pypi.python.org/pypi/edc-export
.. |pypi-edc-facility| image:: https://img.shields.io/pypi/v/edc-facility.svg
    :target: https://pypi.python.org/pypi/edc-facility
.. |pypi-edc-fieldsets| image:: https://img.shields.io/pypi/v/edc-fieldsets.svg
    :target: https://pypi.python.org/pypi/edc-fieldsets
.. |pypi-edc-form-describer| image:: https://img.shields.io/pypi/v/edc-form-describer.svg
    :target: https://pypi.python.org/pypi/edc-form-describer
.. |pypi-edc-form-label| image:: https://img.shields.io/pypi/v/edc-form-label.svg
    :target: https://pypi.python.org/pypi/edc-form-label
.. |pypi-edc-form-runners| image:: https://img.shields.io/pypi/v/edc-form-runners.svg
    :target: https://pypi.python.org/pypi/edc-form-runners
.. |pypi-edc-form-validators| image:: https://img.shields.io/pypi/v/edc-form-validators.svg
    :target: https://pypi.python.org/pypi/edc-form-validators
.. |pypi-edc-glucose| image:: https://img.shields.io/pypi/v/edc-glucose.svg
    :target: https://pypi.python.org/pypi/edc-glucose
.. |pypi-edc-he| image:: https://img.shields.io/pypi/v/edc-he.svg
    :target: https://pypi.python.org/pypi/edc-he
.. |pypi-edc-identifier| image:: https://img.shields.io/pypi/v/edc-identifier.svg
    :target: https://pypi.python.org/pypi/edc-identifier
.. |pypi-edc-lab| image:: https://img.shields.io/pypi/v/edc-lab.svg
    :target: https://pypi.python.org/pypi/edc-lab
.. |pypi-edc-lab-dashboard| image:: https://img.shields.io/pypi/v/edc-lab-dashboard.svg
    :target: https://pypi.python.org/pypi/edc-lab-dashboard
.. |pypi-edc-lab-panel| image:: https://img.shields.io/pypi/v/edc-lab-panel.svg
    :target: https://pypi.python.org/pypi/edc-lab-panel
.. |pypi-edc-lab-results| image:: https://img.shields.io/pypi/v/edc-lab-results.svg
    :target: https://pypi.python.org/pypi/edc-lab-results
.. |pypi-edc-label| image:: https://img.shields.io/pypi/v/edc-label.svg
    :target: https://pypi.python.org/pypi/edc-label
.. |pypi-edc-list-data| image:: https://img.shields.io/pypi/v/edc-list-data.svg
    :target: https://pypi.python.org/pypi/edc-list-data
.. |pypi-edc-listboard| image:: https://img.shields.io/pypi/v/edc-listboard.svg
    :target: https://pypi.python.org/pypi/edc-listboard
.. |pypi-edc-locator| image:: https://img.shields.io/pypi/v/edc-locator.svg
    :target: https://pypi.python.org/pypi/edc-locator
.. |pypi-edc-ltfu| image:: https://img.shields.io/pypi/v/edc-ltfu.svg
    :target: https://pypi.python.org/pypi/edc-ltfu
.. |pypi-edc-metadata| image:: https://img.shields.io/pypi/v/edc-metadata.svg
    :target: https://pypi.python.org/pypi/edc-metadata
.. |pypi-edc-mnsi| image:: https://img.shields.io/pypi/v/edc-mnsi.svg
    :target: https://pypi.python.org/pypi/edc-mnsi
.. |pypi-edc-microbiology| image:: https://img.shields.io/pypi/v/edc-microbiology.svg
    :target: https://pypi.python.org/pypi/edc-microbiology
.. |pypi-edc-microscopy| image:: https://img.shields.io/pypi/v/edc-microscopy.svg
    :target: https://pypi.python.org/pypi/edc-microscopy
.. |pypi-edc-model| image:: https://img.shields.io/pypi/v/edc-model.svg
    :target: https://pypi.python.org/pypi/edc-model
.. |pypi-edc-model-admin| image:: https://img.shields.io/pypi/v/edc-model-admin.svg
    :target: https://pypi.python.org/pypi/edc-model-admin
.. |pypi-edc-model-fields| image:: https://img.shields.io/pypi/v/edc-model-fields.svg
    :target: https://pypi.python.org/pypi/edc-model-fields
.. |pypi-edc-model-form| image:: https://img.shields.io/pypi/v/edc-model-form.svg
    :target: https://pypi.python.org/pypi/edc-model-form
.. |pypi-edc-model-to-dataframe| image:: https://img.shields.io/pypi/v/edc-model-to-dataframe.svg
    :target: https://pypi.python.org/pypi/edc-model-to-dataframe
.. |pypi-edc-navbar| image:: https://img.shields.io/pypi/v/edc-navbar.svg
    :target: https://pypi.python.org/pypi/edc-navbar
.. |pypi-edc-next-appointment| image:: https://img.shields.io/pypi/v/edc-next-appointment.svg
    :target: https://pypi.python.org/pypi/edc-next-appointment
.. |pypi-edc-notification| image:: https://img.shields.io/pypi/v/edc-notification.svg
    :target: https://pypi.python.org/pypi/edc-notification
.. |pypi-edc-offstudy| image:: https://img.shields.io/pypi/v/edc-offstudy.svg
    :target: https://pypi.python.org/pypi/edc-offstudy
.. |pypi-edc-pdutils| image:: https://img.shields.io/pypi/v/edc-pdutils.svg
    :target: https://pypi.python.org/pypi/edc-pdutils
.. |pypi-edc-pharmacy| image:: https://img.shields.io/pypi/v/edc-pharmacy.svg
    :target: https://pypi.python.org/pypi/edc-pharmacy
.. |pypi-edc-prn| image:: https://img.shields.io/pypi/v/edc-prn.svg
    :target: https://pypi.python.org/pypi/edc-prn
.. |pypi-edc-protocol| image:: https://img.shields.io/pypi/v/edc-protocol.svg
    :target: https://pypi.python.org/pypi/edc-protocol
.. |pypi-edc-protocol-incident| image:: https://img.shields.io/pypi/v/edc-protocol-incident.svg
    :target: https://pypi.python.org/pypi/edc-protocol-incident
.. |pypi-edc-pylabels| image:: https://img.shields.io/pypi/v/edc-pylabels.svg
    :target: https://pypi.python.org/pypi/edc-pylabels
.. |pypi-edc-qol| image:: https://img.shields.io/pypi/v/edc-qol.svg
    :target: https://pypi.python.org/pypi/edc-qol
.. |pypi-edc-randomization| image:: https://img.shields.io/pypi/v/edc-randomization.svg
    :target: https://pypi.python.org/pypi/edc-randomization
.. |pypi-edc-refusal| image:: https://img.shields.io/pypi/v/edc-refusal.svg
    :target: https://pypi.python.org/pypi/edc-refusal
.. |pypi-edc-registration| image:: https://img.shields.io/pypi/v/edc-registration.svg
    :target: https://pypi.python.org/pypi/edc-registration
.. |pypi-edc-reportable| image:: https://img.shields.io/pypi/v/edc-reportable.svg
    :target: https://pypi.python.org/pypi/edc-reportable
.. |pypi-edc-pdf-reports| image:: https://img.shields.io/pypi/v/edc-pdf-reports.svg
    :target: https://pypi.python.org/pypi/edc-pdf-reports
.. |pypi-edc-qareports| image:: https://img.shields.io/pypi/v/edc-qareports.svg
    :target: https://pypi.python.org/pypi/edc-qareports
.. |pypi-edc-review-dashboard| image:: https://img.shields.io/pypi/v/edc-review-dashboard.svg
    :target: https://pypi.python.org/pypi/edc-review-dashboard
.. |pypi-edc-rx| image:: https://img.shields.io/pypi/v/edc-rx.svg
    :target: https://pypi.python.org/pypi/edc-rx
.. |pypi-edc-screening| image:: https://img.shields.io/pypi/v/edc-screening.svg
    :target: https://pypi.python.org/pypi/edc-screening
.. |pypi-edc-search| image:: https://img.shields.io/pypi/v/edc-search.svg
    :target: https://pypi.python.org/pypi/edc-search
.. |pypi-edc-sites| image:: https://img.shields.io/pypi/v/edc-sites.svg
    :target: https://pypi.python.org/pypi/edc-sites
.. |pypi-edc-subject-dashboard| image:: https://img.shields.io/pypi/v/edc-subject-dashboard.svg
    :target: https://pypi.python.org/pypi/edc-subject-dashboard
.. |pypi-edc-test-utils| image:: https://img.shields.io/pypi/v/edc-test-utils.svg
    :target: https://pypi.python.org/pypi/edc-test-utils
.. |pypi-edc-timepoint| image:: https://img.shields.io/pypi/v/edc-timepoint.svg
    :target: https://pypi.python.org/pypi/edc-timepoint
.. |pypi-edc-transfer| image:: https://img.shields.io/pypi/v/edc-transfer.svg
    :target: https://pypi.python.org/pypi/edc-transfer
.. |pypi-edc-unblinding| image:: https://img.shields.io/pypi/v/edc-unblinding.svg
    :target: https://pypi.python.org/pypi/edc-unblinding
.. |pypi-edc-utils| image:: https://img.shields.io/pypi/v/edc-utils.svg
    :target: https://pypi.python.org/pypi/edc-utils
.. |pypi-edc-view-utils| image:: https://img.shields.io/pypi/v/edc-view-utils.svg
    :target: https://pypi.python.org/pypi/edc-view-utils
.. |pypi-edc-visit-schedule| image:: https://img.shields.io/pypi/v/edc-visit-schedule.svg
    :target: https://pypi.python.org/pypi/edc-visit-schedule
.. |pypi-edc-visit-tracking| image:: https://img.shields.io/pypi/v/edc-visit-tracking.svg
    :target: https://pypi.python.org/pypi/edc-visit-tracking
.. |pypi-edc-vitals| image:: https://img.shields.io/pypi/v/edc-vitals.svg
    :target: https://pypi.python.org/pypi/edc-vitals
.. |jet-brains| image:: https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.png
    :target: https://jb.gg/OpenSource
    :width: 25
    :alt: JetBrains PyCharm

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |django-packages| image:: https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26
    :target: https://djangopackages.org/packages/p/clinicedc/
