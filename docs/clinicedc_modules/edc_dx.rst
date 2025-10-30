edc-dx
======

Classes to manage review of HIV, DM and HTN diagnoses

Add settings attribute with the conditions to be managed by the `Diagnosis` class.

For example:

.. code-block:: python

    # settings.py
    # ...
    EDC_DX_LABELS = dict(
        hiv="HIV",
        dm="Diabetes",
        htn="Hypertension",
        chol="High Cholesterol"
    )
    # ...
