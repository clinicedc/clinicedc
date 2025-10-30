edc-model-to-dataframe
======================

``ModelToDataframe`` exports EDC subject data into a pandas dataframe. On export it will add ``subject_identifier`` and
visit tracking columns specific to the EDC. Also, by default, encrypted fields are not exported.

M2M columns are joined into a single field value delimited by comma.

Note: If you are just exporting raw tables, use `django_pandas <https://github.com/chrisdev/django-pandas>`__ ``read_frame``.


Pass a model name:

.. code-block:: python

    from django.apps import apps as django_apps
    from edc_model_to_dataframe import ModelToDataframe

    model = "meta_subject.followupexaminiation"
    m = ModelToDataframe(model)
    df = m.dataframe

Pass a queryset:

.. code-block:: python

    # using a queryset
    model_cls = django_apps.get_model("meta_subject.followupexaminiation")
    m = ModelToDataframe(model_cls.objects.all())
    df = m.dataframe


``read_frame_edc``:  like in `django_pandas <https://github.com/chrisdev/django-pandas>`__, there is a ``read_frame`` -like function which wraps ModelToDataframe


.. code-block:: python

    from edc_model_to_dataframe import read_frame_edc

    model_cls = django_apps.get_model(model)
    df = read_frame_edc(model_cls.objects.all())
