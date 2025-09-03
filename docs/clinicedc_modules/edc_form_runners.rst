edc-form-runners
================

Classes to manually run modelform validation for clinicedc/edc projects.


The ``FormRunner`` class
++++++++++++++++++++++++

You can use the ``FormRunner`` to rerun modelform validation on all instances of a model.

For example:

.. code-block:: python

    runner = FormRunner("intecomm_subject.vitals")
    runner.run_all()

This re-runs ``form.is_valid()`` for all instances of ``intecomm_subject.vitals``.
If the Vitals ``ModelForm`` does not validate, the ``FormRunner`` stores each error
of the ``form.errors`` dictionary in model ``Issue`` where
one instance of ``Issue`` is created per field_name:error_message pair.

`Note: Your model must be registered with Admin.`

``run_form_runners``
++++++++++++++++++++

You can run a ``FormRunner`` for every CRF/Requisition model in a module:

.. code-block:: python

    from django.apps import apps as django_apps
    from edc_form_runners.run_form_runners import run_form_runners

    run_form_runners(app_labels=["intecomm_subject"])


or just list a few models explicitly:

.. code-block:: python

    from django.apps import apps as django_apps
    from edc_form_runners.run_form_runners import run_form_runners

    run_form_runners(model_names=["intecomm_subject.vitals", "intecomm_subject.medications"])


Custom FormRunners
++++++++++++++++++

You may wish to ignore some errors; that is, prevent ``FormRunner`` from creating an ``Issue`` instance
for specific fields that do not validate. To do this create a custom ``FormRunner`` for your model
and list the field names to exclude:

.. code-block:: python

    class HtnMedicationAdherenceFormRunner(FormRunner):
        model_name = "intecomm_subject.htnmedicationadherence"
        exclude_formfields = ["pill_count"]


Now you can use the custom ``FormRunner``:

.. code-block:: python

    runner = HtnMedicationAdherenceFormRunner()
    runner.run_all()

if field ``pill_count`` does not validate, the error message will not be written to the ``Issues`` table.

Registering Custom FormRunners
++++++++++++++++++++++++++++++

A custom ``FormRunner`` must be registered to be used by ``edc_form_runners``.

Declare your custom ``FormRunnners`` in module ``form_runners.py`` in the root of your app:

.. code-block:: python

    # form_runners.py
    from edc_form_runners.decorators import register
    from edc_form_runners.form_runner import FormRunner


    @register
    class HtnMedicationAdherenceFormRunner(FormRunner):
        model_name = "intecomm_subject.htnmedicationadherence"
        exclude_formfields = ["pill_count"]

    @register
    class DmMedicationAdherenceFormRunner(FormRunner):
        model_name = "intecomm_subject.dmmedicationadherence"
        exclude_formfields = ["pill_count"]


The ``register`` decorator registers the custom classes with ``site_form_runners``.


``get_form_runner``
+++++++++++++++++++

``edc_form_runners`` gets ``FormRunners`` using ``get_form_runner``.
Given a model name in ``label_lower`` format, ``get_form_runner`` checks the site global (``site_form_runners``) and returns
a custom ``FormRunner``, if it exists, otherwise returns the default ``FormRunner``.

In your code you should use ``get_form_runner``:

.. code-block:: python

    # good, returned DmMedicationAdherenceFormRunner instead of the default FormRunner
    runner = get_form_runner("intecomm_subject.dmmedicationadherence")
    runner.run()

    # works but does not use your custom form runner
    runner = FormRunner("intecomm_subject.dmmedicationadherence")
    runner.run_all()


Management Command ``run_form_runners``
+++++++++++++++++++++++++++++++++++++++

You can use the management command ``run_form_runners`` to run form runners for some or
all CRF/Requisitions. Run this command to initially populate ``Issue`` table and whenever you
change validation logic for a form.

Pass the management command one or more app_labels separated by comma:

.. code-block:: bash

    >>> python manage.py run_form_runners -a intecomm_subject

or pass one or more model names (label_lower format) separated by comma:

.. code-block:: bash

    >>> python manage.py run_form_runners -m intecomm_subject.vitals,intecomm_subject.dmmedicationadherence

You can skip a model as well:

.. code-block:: bash

    >>> python manage.py run_form_runners -a intecomm_subject -s intecomm_subject.medicationadherence

``Issue`` ChangeList
++++++++++++++++++++

The ``ChangeList`` for the ``Issue model`` is available in ``edc_data_manager`` and ``edc_form_runners``.
You would typically use the one in ``edc_data_manager``.

From the change list you can:

* search, filter and re-order
* refresh selected ``Issue`` instances from the action menu.
* navigate to a subject`s dashboard

Integrated with the Subject Dashboard
+++++++++++++++++++++++++++++++++++++

The subject dashboard shows an "Issues" badge next to a CRF or Requisition if one exists. You can
hover over the badge to see some of the error messages detected when the ``FormRunner`` last ran.

If a user edits a CRF with a detected issue and the corrected form validates withour error, the
``Issue`` instance is deleted and the badge is no longer displayed.
(See also ``signals.py``)


``FormRunner`` is ``clinicedc`` specific
++++++++++++++++++++++++++++++++++++++++
At the moment, the ``FormRunner`` class is currently ``clinicedc`` specific in that it only works for models with a
``subject_identifier`` or related_visit FK (e.g. ``subject_visit``).

The ``post_save`` signal that updates Issues listens for ``clinicedc`` CRFs and Requisitions by testing if the model instance
is an instance of ``CrfModelMixin``, ``CrfNoManagerModelMixin`` or ``RequisitionModelMixin``.
