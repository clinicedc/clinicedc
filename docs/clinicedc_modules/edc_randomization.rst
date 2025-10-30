edc-randomization
=================

Randomization objects for clinicedc projects

Overview
++++++++

The ``Randomizer`` class emulates the randomization of a clincial trial participant in
realtime. This module doesn't actually `randomize` in realtime. Instead, a CSV file is
prepared in advance by the statistician. This CSV file lists the order in which subjects
are to be randomized. The ``Randomizer`` class initially imports the entire list in order
into a ``model``. When a subject is to be randomized, the ``Randomizer`` class selects
the next available row from the model.

A very basic ``randomization_list.csv`` prepared in advance might look like this::

    site_name,sid,assignment
    temeke,1000,active
    temeke,1001,active
    temeke,1002,placebo
    temeke,1003,active
    temeke,1004,placebo
    temeke,1005,placebo
    ...

For large multisite trials this may be thousands of lines ordered using some type of block
randomization.

This module will import (only once) all rows from the CSV file into a model. The ``Randomizer``
class selects and allocates in order by site_name one row per participant from the model.

.. code-block:: python

    options = {}
    randomizer_cls = site_randomizers.get("default")
    randomizer_cls.randomize(subject_identifier=subject_identifier, **options)
    # or just:
    site_randomizers.randomize("default", subject_identifier=subject_identifier, **options)

Usually, the ``Randomizer`` class is instantiated in a ``signal`` once the subject's
eligibility is confirmed and the subject's informed consent is submitted. A
`signal` attached to the subject's informed consent is a good place to do this assuming the sequence
of events are 1) pass eligibility criteria, 2) complete informed consent, 3) `randomize` and
issue study identifier 4) start baseline visit.

.. code-block:: python

    @receiver(
        post_save,
        weak=False,
        sender=SubjectConsent,
        dispatch_uid="subject_consent_on_post_save",
    )
    def subject_consent_on_post_save(sender, instance, raw, created, **kwargs):
        if not raw:
            if created:
                # ...
                # randomize
                site_randomizers.randomize(
                    "default",
                    subject_identifier=instance.subject_identifier,
                    report_datetime=instance.consent_datetime,
                    site=instance.site,
                    user=instance.user_created,
                )
                #...


Registering a randomizer
++++++++++++++++++++++++
The default ``Randomizer`` class is ``edc_randomization.randomizer.Randomizer``. Unless you
indicate otherwise, it will be automatically registered with the site controller,
``site_randomizers`` with the name ``default``. It is recommended you access the ``Randomizer``
class through ``site_randomizers`` instead of directly importing.

.. code-block:: python

    randomizer_cls = site_randomizers.get("default")


Customizing the default randomizer
++++++++++++++++++++++++++++++++++

Some attributes of the default ``Randomizer`` class can be customized using ``settings`` attributes:

.. code-block:: python

    EDC_RANDOMIZATION_LIST_PATH = 'path/to/csv_file'
    EDC_RANDOMIZATION_ASSIGNMENT_MAP = {
        "intervention": 1,
        "control": 2,
        }
    EDC_RANDOMIZATION_ASSIGNMENT_DESCRIPTION_MAP = {
        "intervention": "Fluconazole plus flucytosine",
        "control": "Fluconazole"
        }

Creating a custom randomizer
++++++++++++++++++++++++++++

If you need to customize further, create a custom ``Randomizer`` class.

In the example below, ``gender`` is added for a trial stratified by ``gender``.

Custom ``Randomizer`` classes live in ``randomizers.py`` in the root of your app. The
``site_randomizers`` controller will ``autodiscover`` them.

.. code-block:: python

    # my_app/randomizers.py

    @register()
    class MyRandomizer(Randomizer):
        name = "my_randomizer"
        model = "edc_randomization.myrandomizationlist"
        randomization_list_path = tmpdir
        assignment_map = {"Intervention": 1, "Control": 0}
        assignment_description_map = {"Intervention": "Fluconazole plus flucytosine", "Control": "Fluconazole"}
        extra_csv_fieldnames = ["gender"]

        def __init__(self, gender=None, **kwargs):
            self.gender = gender
            super().__init__(**kwargs)

        @property
        def extra_required_instance_attrs(self):
            return dict(gender=self.gender)

        @property
        def extra_model_obj_options(self):
            return dict(gender=self.gender)

        @classmethod
        def get_extra_list_display(cls):
            return [(4, "gender")]


The ``register()`` decorator registers the custom class with ``site_randomizers``.

With a custom randomizer, the default ``Randomizer`` class is no longer needed,
update settings to prevent the default class from registering.

Use the settings attribute:

.. code-block:: python

    EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER = False

Confirm this by checking the ``site_randomizers``:

.. doctest:: site_randomizers

    >>> randomizer_cls = site_randomizers.get("default")
    NotRegistered: A Randomizer class by this name ...

    >>> randomizer_cls = site_randomizers.get("my_randomizer")
    >>> randomizer_cls.name
    "my_randomizer"


Manually Importing from CSV
+++++++++++++++++++++++++++
A ``Randomizer`` class will call ``import_list`` when it is instantiated
for the first time. If you want to load the CSV file manually,
import the ``Randomizer`` class and call ``import_list()``.


.. doctest:: import_list1

   >>> randomizer_cls = site_randomizers.get("my_randomizer")
   >>> randomizer_cls.import_list()
   Import CSV data
     Randomizer:
       -  Name: my_randomizer
       -  Assignments: {'active': 1, 'placebo': 2}
       -  Model: edc_randomization.myrandomizationlist
       -  Path: /home/me/.etc/randomization_list.csv
       -  Imported 5 SIDs for randomizer `my_randomizer` into model `edc_randomization.myrandomizationlist`
          from /home/me/.etc/randomization_list.csv.
       -  Verified OK.

Manually Importing additional slots added to the original CSV
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Add additional records to the end of the CSV file referred to by the ``randomizer_cls`` then call ``import_list(add=True)``.

.. doctest:: import_list2

   >>> randomizer_cls = site_randomizers.get("my_randomizer")
   >>> randomizer_cls.import_list(add=True)
   Import CSV data
     Randomizer:
       -  Name: my_randomizer
       -  Assignments: {'active': 1, 'placebo': 2}
       -  Model: edc_randomization.myrandomizationlist
       -  Path: /home/me/.etc/randomization_list.csv
       -  Imported 5 SIDs for randomizer `my_randomizer` into model `edc_randomization.myrandomizationlist`
          from /home/me/.etc/randomization_list.csv.
       -  Verified OK.



Manually Export to CSV
++++++++++++++++++++++

.. code-block:: python

    >>> from edc_randomization.utils import export_randomization_list
    >>> export_randomization_list(randomizer_name="default",path="~/", username="erikvw")

If the user does not have permissions to view the randomizationlist table, a ``RandomizationListExporterError`` will be raised::

    RandomizationListExporterError: User `erikvw` does not have permission to view 'edc_randomization.randomizationlist'
