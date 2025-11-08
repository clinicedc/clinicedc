edc-export
==========

You can export clinicedc models using ``ModelsToFile``. You need to load the django environment in order to use this class.

If you are running a notebook you can load the DJANGO environment likes this:

.. code-block:: python

    # %%capture
    import os
    import pandas as pd
    from dj_notebook import activate
    from pathlib import Path

    env_file = os.environ["META_ENV"] # path to .env file

    plus = activate(dotenv_file=env_file)
    pd.set_option('future.no_silent_downcasting', True)


Note:
    If you cannot load the Django environment try ``clinicedc_utils`` function ``export_raw_tables`` instead of ``ModelsToFile``. Function ``export_raw_tables`` passes simple SELECT ALL statements for each model in a project to pandas ``read_sql`` to generate CSV and STATA files. However, ``export_raw_tables`` does not expand foreign keys and M2M columns.

Exporting a clinicedc projects models
+++++++++++++++++++++++++++++++++++++

``ModelsToFile`` creates dataframes for each model and exports to either CSV or STATA (118) using pandas ``to_csv`` or ``to_stata``. Each dataframe is created using class ``ModelToDataframe``. ``ModelToDataframe`` attempts to convert datatypes (datetime, int, float, string) and:

* adds subject_identifier, gender, dob to every longitudinal model
* expands M2M columns to a comma separated list of responses
* expands FK relations for list models to the "name" field of the FK

To export all relevant models from a typical clinicedc project:

.. code-block:: python

    from django.apps import apps as django_apps
    from edc_export.models_to_file import ModelsToFile
    from django.contrib.auth.models import User
    from edc_export.constants import CSV, STATA_14
    from edc_sites.site import sites

    #%%

    # user's permissions are checked per model and site when exporting
    user = User.objects.get(username="erikvw")

    # grab a list of all sites, not just the current
    site_ids = list(sites.all().keys())

    #%%
    study_prefix = "meta"
    study_apps = [
        f"{study_prefix}_consent",
        f"{study_prefix}_lists",
        f"{study_prefix}_subject",
        f"{study_prefix}_ae",
        f"{study_prefix}_prn",
        f"{study_prefix}_screening",
    ]
    all_model_names = [
        "edc_appointment.appointment",
        "edc_data_manager.datadictionary",
        "edc_metadata.crfmetadata",
        "edc_metadata.requisitionmetadata",
        "edc_registration.registeredsubject",
        "edc_visit_schedule.subjectschedulehistory",
    ]

    excluded_model_names = []

    #%%
    # prepare a list of model names in label lower format
    for app_config in django_apps.get_app_configs():
        if app_config.name.startswith(study_prefix):
            if app_config.name in study_apps:
                model_names = [
                    model_cls._meta.label_lower
                    for model_cls in app_config.get_models()
                    if "historical" not in model_cls._meta.label_lower
                    and not model_cls._meta.proxy
                    and model_cls._meta.label_lower not in excluded_model_names
                ]
                if model_names:
                    all_model_names.extend(model_names)


    #%%
    # export to dataframe then CSV; then add all CSV files to a ZIP archive
    models_to_file = ModelsToFile(
        user=user,
        models=all_model_names,
        site_ids=site_ids,
        decrypt=False,
        archive_to_single_file=True,
        export_format=CSV
    )

    # archive (zip) will be in a temp folder. Copy the path and move the file to a more convenient location.
    print(models_to_file.archive_filename)
