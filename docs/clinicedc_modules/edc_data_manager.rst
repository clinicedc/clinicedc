edc-data-manager
================

Data manager administrative models and classes.

``edc-data-manager`` adds models and functionality to the Edc that compliment the role of the clinical trial data manager.
The ``Data Query`` form guides the data manager in describing missing, incomplete or incorrect participant data. The ``Data Query``
is then made available to research staff on the participant's dashboard and administrative pages. Additionally, the data manager
can define ``Query Rules`` that scan the dataset for participant data that match the rule's criteria. For each match found,
``edc-data-manager`` automatically creates a ``Data Query``.

For automated queries, those created when a ``Query Rule`` is run, ``edc-data-manager`` will re-run a ``Query Rule`` upon updates
to the participant data. If the criteria is no longer met, the ``Data Query`` is automatically closed.


User Roles
----------

``edc_data_manager`` adds the ``DATA MANAGER`` and the ``DATA_QUERY`` user groups.
Members of the ``DATA_QUERY`` group can respond to existing data queries by completing  the "site response" section of the form.
They do not have permissions to change the criteria of the data query. Research staff responsible for submitting participant
data are typically given membership to the ``DATA_QUERY`` user group.


Members of the ``DATA MANAGER`` user group can add/change/delete any ``Data Query`` form and ``Query Rule`` form.
Data managers, those who oversee data collection but do not submit data themselves, are typically members of the ``DATA MANAGER`` user group.


The Data Query Model
--------------------
The central model of ``edc_data_manager`` is the ``Data Query`` model. A ``Data Query`` is either created manually by a data manager
or automatically when a ``Query Rule`` is run. The ``data query`` describes an issue for the attention of the research staff.
A data query might be general, describing the issue with nothing more than a free text comment, or specific. To allow for a specific
data query, the ``Query Rule`` form has questions where the data manager (or ``Query Rule``) can select the relevant timepoints, form questions,
and timing.

Data query status
+++++++++++++++++

The ``Data Query`` status is split between two fields, one managed by the research staff and one by the data manager. Initially the
research staff status is set to ``New`` and the data manager's status is set to ``Open``.

The available states of a ``Data Query`` are similar to those used on ticketing systems; namely, New, Open , Feedback, Resolved, Closed.
Only a data manager can close a data query.

Members of the ``DATA_QUERY`` group can:

* Open the query -- indicating they are working on the issue. (``Open``)
* Request feedback -- indicating they need assistance from the data manager .(``Feedback``)
* Resolve the query -- indicating the issue is resolved. (``Resolved``)

This status field, managed by members of the ``DATA_QUERY`` group, is in a seperate section of the ``Data Query`` form.

Members of the ``DATA_MANAGER`` have their own section on the form and can:

* Resolve the query (but only if the site status is also ``Resolved``)
* Resolve with an action plan

Since data managers have full permissions to the form, they can override the status set by the research staff.

Query Rules
-----------

Query Rules define criteria to be used to scan the dataset for data problems. In a query rule you can define the following:

* CRF model
* Related requisition panel name (if applicable)
* CRF questions
* Timepoints (visits)
* Timing (when to run the query, e.g. 48 hours after the visit report is submitted)
* Priority
* Research staff contact
* Data manager contact

As mentioned above, a ``Data Query`` can be automatically created by a ``Query Rule``. Simple ``Query Rules`` are defined using the ``Query Rule`` form.
``Query Rules`` are run by a "handler". The default handler is sufficient in most cases. If not, a custom handler can be written, registered with
``edc_data_manager``, and selected on the ``Query Rule`` form.

When are Query Rules run?
+++++++++++++++++++++++++

* Query rules can be run as an Admin action from the QueryRule Admin page;
* A Query rule is run when a model is modified;
* Query rules can be scheduled if ``django-celery`` is installed.

Data Queries trigger action items
+++++++++++++++++++++++++++++++++

When a data query is created, a supporting action item is also created. As with all action items, this means an "alert"
shows on the participant dashboard and users can be notified by email and/or SMS. See ``edc_action_item``.


QueryRuleHandler -- the default rule handler
++++++++++++++++++++++++++++++++++++++++++++

For each timepoint specified in the ``Query Rule``, the handler:

* checks to see if the visit report has been submitted. If not, the rule is ignored.
* checks if the requisition has been completed (if a requisition panel is linked to the query rule). If the requisition has not been completed, a ``Data Query`` is created immediately.
* gathers each value specified in the list of CRF form questions and calls ``inspect_model``.
* if ``inspect_model`` returns False, the ``Data Query`` is created or re-opened.
* if ``inspect_model`` returns True, no data query is created or the existing ``Data Query`` is resolved.

Custom rule handlers
++++++++++++++++++++

The default rule handler, ``QueryRuleHandler``, already does a lot, but it cannot satisfy all cases. The default ``inspect_model`` method
does most of the form specific work of ``QueryRuleHandler``. In the default implementation of ``inspect_model``, a blank field value is
considered invalid and ``inspect_model`` returns ``False``. This may be fine if the ``Query Rule`` is just looking for just a single field value
but not for a combination of values. When looking for a combination of field values, a blank field value may be valid. In such cases
you can override the ``inspect_model`` method and specify the correct logic for the desired data condition.

For example:

.. code-block:: python

    # data_manager.py

    from ambition_subject.constants import AWAITING_RESULTS
    from edc_constants.constants import NOT_DONE, YES, NO
    from edc_data_manager.handlers import QueryRuleHandler
    from edc_data_manager.site_data_manager import site_data_manager


    class LumbarPunctureHandlerQ13(QueryRuleHandler):

        name = "lumbar_puncture_q13"
        display_name = "Lumbar Puncture (Q13, 15, 21, 23, 24)"
        model_name = "ambition_subject.lumbarpuncturecsf"

        @property
        def inspect_model(self):
            """Lumbar Puncture/Cerebrospinal Fluid 13, 15, 21, 23, 24.
            """
            valid = False
            if self.get_field_value("csf_culture") == AWAITING_RESULTS:
                pass
            elif self.get_field_value("csf_culture") == NOT_DONE:
                valid = True
            elif self.get_field_value("csf_culture") == YES:
                if (self.get_field_value("other_csf_culture")
                        and self.get_field_value("csf_wbc_cell_count")
                        and self.get_field_value("csf_glucose")
                        and self.get_field_value("csf_protein")
                        and (self.get_field_value("csf_cr_ag")
                             or self.get_field_value("india_ink"))):
                    valid = True
            elif self.get_field_value("csf_culture") == NO:
                if (self.get_field_value("csf_wbc_cell_count")
                        and self.get_field_value("csf_glucose")
                        and self.get_field_value("csf_protein")
                        and (self.get_field_value("csf_cr_ag")
                             or self.get_field_value("india_ink"))):
                    valid = True
            return valid

    site_data_manager.register(LumbarPunctureHandlerQ13)

Note the use of ``get_field_value`` method instead of directly accessing the model instance. This is not absolutely necessary but
avoids confusion by ensuring you only access fields defined in the ``Query Rule``.


Registering custom rule handlers
++++++++++++++++++++++++++++++++

``edc_data_manager`` has a site registry that ``autodiscovers`` module ``data_manager.py`` in the root of each app in ``INSTALLED_APPS``.

For example:

.. code-block:: python

    # data_manager.py

    from edc_data_manager.handlers import QueryRuleHandler
    from edc_data_manager.site_data_manager import site_data_manager


    class MyCustomHandler(QueryRuleHandler):

        name = "my_custom_handler"
        display_name = "My Custom Handler"
        model_name = "my_app.somecrf"

        @property
        def inspect_model(self):

            valid = False

            if self.get_field_value("field_one") == 1:
                # ... some more code that eventually sets valid to True
                return my_code_that_returns_true()
            return valid

    site_data_manager.register(MyCustomHandler)

Dumping and loading a QueryRule fixture
++++++++++++++++++++++++++++++++++++++++++

.. code-block:: bash

    python manage.py dumpdata edc_data_manager.queryrule --natural-foreign --natural-primary --indent 4 -o queryrule.json

.. code-block:: bash

    python manage.py loaddata queryrules.json

Updating query rules
++++++++++++++++++++

Query rules can be triggered manually to run from the admin action under the `QueryRule` admin page.

If ``celery`` is enabled, the ``update_query_rules`` will try to send proccessing to the MQ.

See also ``update_query_rules``, ``update_query_rules_action``.

Rerun form validation
=====================

You can use the ``FormValidationRunner`` to rerun form validation on all instances for a model.

You could do this:

.. code-block:: python

    runner = FormValidationRunner(modelform)
    runner.run()


You could also run for every model in your EDC deployment by getting the ``ModelForm`` class
from the ``admin`` registry and running ``FormValidationRunner``:

.. code-block:: python

    from django.apps import apps as django_apps
    from edc_data_manager.form_validation_runners import (
        FormValidationRunner,
        FormValidationRunnerError,
        get_modelform_cls,
        )

    for app_config in django_apps.get_app_configs():
        if app_config.name.startswith("edc_"):
            continue
        for model_cls in app_config.get_models():
            if model_cls == Appointment:
                continue
            print(model_cls._meta.label_lower)
            try:
                modelform = get_modelform_cls(model_cls._meta.label_lower)
            except FormValidationRunnerError as e:
                print(e)
            else:
                print(modelform)
                try:
                    runner = FormValidationRunner(modelform)
                except AttributeError as e:
                    print(f"{e}. See {model_cls._meta.label_lower}.")
                else:
                    try:
                        runner.run()
                    except (AttributeError, FieldError) as e:
                        print(f"{e}. See {model_cls._meta.label_lower}.")


You could also create a custom ``FormValidationRunner`` for your model to add extra fields and ignore others.

For example:

.. code-block:: python

    class AppointmentFormValidationRunner(FormValidationRunner):
        def __init__(self, modelform_cls: ModelForm = None, **kwargs):
            modelform_cls = modelform_cls or AppointmentForm
            extra_fieldnames = ["appt_datetime"]
            ignore_fieldnames = ["appt_close_datetime"]
            super().__init__(
                modelform_cls=modelform_cls,
                extra_formfields=extra_fieldnames,
                ignore_formfields=ignore_fieldnames,
                **kwargs,
            )
