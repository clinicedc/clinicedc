edc-form-describer
==================

Describe edc forms in markdown.

Generate a document describing the forms in an EDC module annotated with field names, table
names, choices, etc.

For example::

    python manage.py make_forms_reference \
        --app_label effect_subject \
        --admin_site effect_subject_admin \
        --visit_schedule visit_schedule


