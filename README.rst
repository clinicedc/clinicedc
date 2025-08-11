
.. attention::

    2025/08/06

    We are in the process of merging all edc modules into this one repo.

    This is a work in progress.

    the stable version of clinicedc / edc is edc v1.2.7


As of 2025/08/06, the stable version of edc is `edc v1.2.7 <https://github.com/clinicedc/edc>`_



|pypi| |actions| |uv| |black| |downloads| |django-packages|

clinicedc -  A clinical trials data management framework built on Django
========================================================================

A data management framework built on Django for multisite randomized longitudinal clinical trials.

Documentation: `clinicedc.readthedocs.io <https://clinicedc.readthedocs.io/>`_

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

|django| |jet-brains|

Thanks to `JetBrains <https://www.jetbrains.com>`_ for support with an opensource PyCharm IDE license.



How we describe the EDC in our protocol documents
-------------------------------------------------

Here is a simple example of a data management section for a study protocol document: `data_management_section`_

.. _data_management_section: https://github.com/clinicedc/edc/blob/main/docs/protocol_data_management_section.rst


Projects that use ``clinicedc``
-------------------------------
Recent examples of ``clinicedc`` applications using this codebase:

INTECOMM Trial
~~~~~~~~~~~~~~
Controlling chronic diseases in Africa: Development and evaluation of an integrated community-based management model for HIV, Diabetes and Hypertension in Tanzania and Uganda

https://github.com/intecomm-trial/intecomm-edc (2022-2025)

EFFECT Trial
~~~~~~~~~~~~
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

MOCCA Trial
~~~~~~~~~~~

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

Optional modules
----------------

=========================== ============================= ==================================
edc-csf_                    |edc-csf|                     |pypi-edc-csf|
edc-dx_                     |edc-dx|                      |pypi-edc-dx|
edc-dx-review_              |edc-dx-review|               |pypi-edc-dx-review|
edc-egfr_                   |edc-egfr|                    |pypi-edc-egfr|
edc-glucose_                |edc-glucose|                 |pypi-edc-glucose|
edc-he_                     |edc-he|                      |pypi-edc-he|
edc-icecap-a_               |edc-icecap-a|                |pypi-edc-icecap-a|
edc-microbiology_           |edc-microbiology|            |pypi-edc-microbiology|
edc-microscopy_             |edc-microscopy|              |pypi-edc-microscopy|
edc-mnsi_                   |edc-mnsi|                    |pypi-edc-mnsi|
edc-phq9_                   |edc-phq9|                    |pypi-edc-phq9|
edc-qol_                    |edc-qol|                     |pypi-edc-qol|
edc-vitals_                 |edc-vitals|                  |pypi-edc-vitals|
edc-test-settings_          |edc-test-settings|           |pypi-edc-test-settings|
edc-test-utils_             |edc-test-utils|              |pypi-edc-test-utils|
=========================== ============================= ==================================


Tests
=====

.. code-block:: bash

    uv venv
    source .venv/bin/activate
    uv sync --group lint --group test
    uv run runtests.py --settings=tests.test_settings

or just

.. code-block:: bash

    uv run --group lint --group test runtests.py --settings=tests.test_settings


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
.. _edc-icecap-a: https://github.com/clinicedc/edc-icecap-a
.. _edc-mnsi: https://github.com/clinicedc/edc-mnsi
.. _edc-microbiology: https://github.com/clinicedc/edc-microbiology
.. _edc-microscopy: https://github.com/clinicedc/edc-microscopy
.. _edc-phq9: https://github.com/clinicedc/edc-phq9
.. _edc-qol: https://github.com/clinicedc/edc-qol
.. _edc-test-settings: https://github.com/clinicedc/edc-test-settings
.. _edc-test-utils: https://github.com/clinicedc/edc-test-utils
.. _edc-vitals: https://github.com/clinicedc/edc-vitals

.. |edc-csf| image:: https://github.com/clinicedc/edc-csf/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-csf/actions/workflows/build.yml
.. |edc-dx| image:: https://github.com/clinicedc/edc-dx/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-dx/actions/workflows/build.yml
.. |edc-dx-review| image:: https://github.com/clinicedc/edc-dx-review/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-dx-review/actions/workflows/build.yml
.. |edc-egfr| image:: https://github.com/clinicedc/edc-egfr/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-egfr/actions/workflows/build.yml
.. |edc-glucose| image:: https://github.com/clinicedc/edc-glucose/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-glucose/actions/workflows/build.yml
.. |edc-he| image:: https://github.com/clinicedc/edc-he/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-he/actions/workflows/build.yml
.. |edc-icecap-a| image:: https://github.com/clinicedc/edc-icecap-a/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-icecap-a/actions/workflows/build.yml
.. |edc-mnsi| image:: https://github.com/clinicedc/edc-mnsi/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-mnsi/actions/workflows/build.yml
.. |edc-microbiology| image:: https://github.com/clinicedc/edc-microbiology/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-microbiology/actions/workflows/build.yml
.. |edc-microscopy| image:: https://github.com/clinicedc/edc-microscopy/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-microscopy/actions/workflows/build.yml
.. |edc-phq9| image:: https://github.com/clinicedc/edc-phq9/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-phq9/actions/workflows/build.yml
.. |edc-qol| image:: https://github.com/clinicedc/edc-qol/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-qol/actions/workflows/build.yml
.. |edc-rx| image:: https://github.com/clinicedc/edc-rx/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-rx/actions/workflows/build.yml
.. |edc-test-settings| image:: https://github.com/clinicedc/edc-test-settings/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-test-settings/actions/workflows/build.yml
.. |edc-test-utils| image:: https://github.com/clinicedc/edc-test-utils/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-test-utils/actions/workflows/build.yml
.. |edc-vitals| image:: https://github.com/clinicedc/edc-vitals/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-vitals/actions/workflows/build.yml

.. |pypi-edc-csf| image:: https://img.shields.io/pypi/v/edc-csf.svg
    :target: https://pypi.python.org/pypi/edc-csf
.. |pypi-edc-dx| image:: https://img.shields.io/pypi/v/edc-dx.svg
    :target: https://pypi.python.org/pypi/edc-dx
.. |pypi-edc-dx-review| image:: https://img.shields.io/pypi/v/edc-dx-review.svg
    :target: https://pypi.python.org/pypi/edc-dx-review
.. |pypi-edc-egfr| image:: https://img.shields.io/pypi/v/edc-egfr.svg
    :target: https://pypi.python.org/pypi/edc-egfr
.. |pypi-edc-glucose| image:: https://img.shields.io/pypi/v/edc-glucose.svg
    :target: https://pypi.python.org/pypi/edc-glucose
.. |pypi-edc-he| image:: https://img.shields.io/pypi/v/edc-he.svg
    :target: https://pypi.python.org/pypi/edc-he
.. |pypi-edc-icecap-a| image:: https://img.shields.io/pypi/v/edc-he.svg
    :target: https://pypi.python.org/pypi/edc-icecap-a
.. |pypi-edc-mnsi| image:: https://img.shields.io/pypi/v/edc-mnsi.svg
    :target: https://pypi.python.org/pypi/edc-mnsi
.. |pypi-edc-microbiology| image:: https://img.shields.io/pypi/v/edc-microbiology.svg
    :target: https://pypi.python.org/pypi/edc-microbiology
.. |pypi-edc-microscopy| image:: https://img.shields.io/pypi/v/edc-microscopy.svg
    :target: https://pypi.python.org/pypi/edc-microscopy
.. |pypi-edc-phq9| image:: https://img.shields.io/pypi/v/edc-phq9.svg
    :target: https://pypi.python.org/pypi/edc-phq9
.. |pypi-edc-qol| image:: https://img.shields.io/pypi/v/edc-qol.svg
    :target: https://pypi.python.org/pypi/edc-qol
.. |pypi-edc-rx| image:: https://img.shields.io/pypi/v/edc-rx.svg
    :target: https://pypi.python.org/pypi/edc-rx
.. |pypi-edc-test-settings| image:: https://img.shields.io/pypi/v/edc-test-settings.svg
    :target: https://pypi.python.org/pypi/edc-test-utils
.. |pypi-edc-test-utils| image:: https://img.shields.io/pypi/v/edc-test-utils.svg
    :target: https://pypi.python.org/pypi/edc-test-utils
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

.. |actions| image:: https://github.com/clinicedc/clinicedc/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/clinicedc/actions/workflows/build.yml

.. |uv| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
  :target: https://github.com/astral-sh/uv
