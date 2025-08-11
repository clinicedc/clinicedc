edc-adverse-event
=================

Create an AE application
------------------------

Create an AE app that will house your AE concrete models, admin site, list data, and action items.

Adverse events models
---------------------

Model mixins exist for you to create the following concrete models in your AE app:

* AE Initial: The initial report of a adverse event
* AE Followup: 1 or more follow-ups to the initial AE report
* AE Special Interest
* AE SUSAR
* AE External Reviewer
* Death Report
* Death Report External Reviewer

TMG: Trial Management Group forms

* AE Tmg:

Settings
--------

These are the ``settings`` attributes you need to define for ``edc_adverse_event``:

.. code-block:: python

    # settings.py

    ...

    ADVERSE_EVENT_APP_LABEL="edc_adverse_event"  # replace with your AE app label
    ADVERSE_EVENT_ADMIN_SITE="edc_adverse_event_admin"  # replave with your AE app admin site name

    ...

Define a list_data.py
---------------------

There are a few FK fields on the AE models. You need to define a ``list_data.py`` that will be read to populate the FK list models.

The list model tables are:
* ``edc_adverse_event.aeclassification`` (See AeInitial)
* ``edc_adverse_event.saereason`` (See AeInitial)

.. code-block:: python

    # list_data.py

    list_data = {
        "edc_adverse_event.aeclassification": [
            (ANAEMIA, "Anaemia"),
            ("diarrhoea", "Diarrhoea"),
            (RENAL_IMPAIRMENT, "Renal impairment"),
            (OTHER, "Other"),
        ],
        "edc_adverse_event.saereason": [
            (NOT_APPLICABLE, "Not applicable"),
            (DEAD, "Death"),
            ("life_threatening", "Life-threatening"),
            ("significant_disability", "Significant disability"),
            (
                "in-patient_hospitalization",
                (
                    "In-patient hospitalization or prolongation "
                    "(17 or more days from study inclusion)"
                ),
            ),
            (
                "medically_important_event",
                "Medically important event (e.g. recurrence of symptoms not requiring admission, "
                "Hospital acquired pneumonia)",
            ),
        ],
    }

    preload_data = PreloadData(
        list_data=list_data, model_data={}, unique_field_data=None)


Register AE Action Items
------------------------

The AE action items are not registered by default. To register, in the root of your AE app add an ``action_items.py``:

.. code-block:: python

    # action_items.py

    from edc_adverse_event.action_items import AeInitialAction
    from edc_adverse_event.action_items import AeFollowupAction
    from edc_adverse_event.action_items import AeSusarAction
    from edc_adverse_event.action_items import AeTmgAction

    site_action_items.register(AeInitialAction)
    site_action_items.register(AeFollowupAction)
    site_action_items.register(AeTmgAction)
    site_action_items.register(AeSusarAction)

