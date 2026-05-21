edc-lab-results
===============

Simple blood result data collection format for django models

In this design
    * a specimen requisition for a panel is completed first (SubjectRequisition)
    * result is received and entered into a result form
    * if a result is admnormal or gradable, an ActionItem is created.

Building the Model
------------------

Below we create a model class with ``BloodResultsModelMixin``. On the class we specify the ``lab_panel`` and limit the FK the requisitions of this panel using ``limit_choices_to``.

.. code-block:: python

    # models.py

    from edc_lab.model_mixins import CrfWithRequisitionModelMixin, requisition_fk_options
    from edc_lab_panels.panels import chemistry_panel

    class BloodResultsFbc(
        CrfWithRequisitionModelMixin,
        BloodResultsModelMixin,
        BaseUuidModel,
    ):

        lab_panel = fbc_panel

        requisition = models.ForeignKey(
            limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
        )

        class Meta(CrfWithActionModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Blood Result: FBC"
            verbose_name_plural = "Blood Results: FBC"

The above example has no fields for results, so let's add some model mixins, one for each result item.

.. code-block:: python

    # models.py

    class BloodResultsFbc(
        CrfWithRequisitionModelMixin,
        HaemoglobinModelMixin,
        HctModelMixin,
        RbcModelMixin,
        WbcModelMixin,
        PlateletsModelMixin,
        MchModelMixin,
        MchcModelMixin,
        McvModelMixin,
        BloodResultsModelMixin,
        CrfStatusModelMixin,
        BaseUuidModel,
    ):

        lab_panel = fbc_panel

        requisition = models.ForeignKey(
            limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
        )

        class Meta(CrfWithActionModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Blood Result: FBC"
            verbose_name_plural = "Blood Results: FBC"

If an ``ActionItem`` is to be created because of an abnormal or reportable result item, add the ActionItem.

.. code-block:: python

    # models.py

    class BloodResultsFbc(
        CrfWithActionModelMixin,
        CrfWithRequisitionModelMixin,
        HaemoglobinModelMixin,
        HctModelMixin,
        RbcModelMixin,
        WbcModelMixin,
        PlateletsModelMixin,
        MchModelMixin,
        MchcModelMixin,
        McvModelMixin,
        BloodResultsModelMixin,
        CrfStatusModelMixin,
        BaseUuidModel,
    ):
        action_name = BLOOD_RESULTS_FBC_ACTION

        lab_panel = fbc_panel

        requisition = models.ForeignKey(
            limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
        )

        class Meta(CrfWithActionModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Blood Result: FBC"
            verbose_name_plural = "Blood Results: FBC"

Building the ModeForm class
---------------------------
The ModelForm class just needs the Model class and the panel. In this case ``BloodResultsFbc`` and ``fbc_panel``.

.. code-block:: python

    # forms.py

    class BloodResultsFbcFormValidator(BloodResultsFormValidatorMixin, CrfFormValidator):
        panel = fbc_panel


    class BloodResultsFbcForm(ActionItemCrfFormMixin, CrfModelFormMixin, forms.ModelForm):
        form_validator_cls = BloodResultsFbcFormValidator

        class Meta(ActionItemCrfFormMixin.Meta):
            model = BloodResultsFbc
            fields = "__all__"


Building the ModelAdmin class
-----------------------------

The ModelAdmin class needs the Model class, ModelForm class and the panel.

.. code-block:: python

    # admin.py

    @admin.register(BloodResultsFbc, site=intecomm_subject_admin)
    class BloodResultsFbcAdmin(BloodResultsModelAdminMixin, CrfModelAdmin):
        form = BloodResultsFbcForm
        fieldsets = BloodResultFieldset(
            BloodResultsFbc.lab_panel,
            model_cls=BloodResultsFbc,
            extra_fieldsets=[(-1, action_fieldset_tuple)],
        ).fieldsets


The SubjectRequistion ModelAdmin class
--------------------------------------

When using ``autocomplete`` for the subject requsition FK on the result form ModelAdmin class, the subject requsition model admin class needs to filter the search results passed to the autocomplete control.

If all result models are prefixed with "bloodresult", you can filter on the path name like this:

.. code-block:: python

    # admin.py

    @admin.register(SubjectRequisition, site=intecomm_subject_admin)
    class SubjectRequisitionAdmin(RequisitionAdminMixin, CrfModelAdmin):
        form = SubjectRequisitionForm

        # ...

        def get_search_results(self, request, queryset, search_term):
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            path = urlsplit(request.META.get("HTTP_REFERER")).path
            query = urlsplit(request.META.get("HTTP_REFERER")).query
            if "bloodresult" in str(path):
                attrs = parse_qs(str(query))
                try:
                    subject_visit = attrs.get("subject_visit")[0]
                except (TypeError, IndexError):
                    pass
                else:
                    queryset = queryset.filter(subject_visit=subject_visit, is_drawn=YES)
            return queryset, use_distinct


Importing External Lab Results
------------------------------

``edc_lab_results`` provides management commands and models to import lab results
from external sources (e.g. PDF reports from a hospital laboratory) into the EDC.

Models
~~~~~~

``Result``
    Stores raw parsed lab data. Each row represents one investigation result from a PDF.
    Fields include patient identifiers, specimen details, timestamps, result values,
    units, flags, and reference ranges. A ``utest_id`` field links the result to the
    EDC's internal test identifier. A ``subject_identifier`` field is resolved from
    the ``name_id`` on the PDF via ``RegisteredSubject``.

``InvestigationMapping``
    Persists the mapping between a laboratory's investigation name (as printed on the PDF)
    and the EDC ``utest_id``. Scoped by ``laboratory`` so the same investigation name can
    map differently at different labs. An ``in_reportable`` boolean records whether the
    ``utest_id`` exists in ``edc_reportable.NormalData``.

Settings
~~~~~~~~

Two settings control the import behavior:

``EDC_LAB_RESULTS_PARSERS``
    A dict mapping laboratory names to dotted paths of parser callables. Each parser
    must accept ``(folder, *, tz=None)`` and return a ``pandas.DataFrame``.

    .. code-block:: python

        # settings.py

        EDC_LAB_RESULTS_PARSERS = {
            "MNH": "parse_trial_labs.parse_folder",
        }

``EDC_LAB_RESULTS_DEFAULT_MAPPINGS``
    A dict of dicts providing default investigation-to-utest_id mappings per laboratory.
    Used as best guesses during the interactive prompt when no saved mapping exists.

    .. code-block:: python

        # settings.py

        EDC_LAB_RESULTS_DEFAULT_MAPPINGS = {
            "MNH": {
                "WBC": "wbc",
                "RBC": "rbc",
                "HGB": "haemoglobin",
                "CREATININE": "creatinine",
                "CHOLESTEROL": "chol",
                # ...
            },
        }

Writing a Custom Parser
~~~~~~~~~~~~~~~~~~~~~~~

A parser is any callable with the signature:

.. code-block:: python

    def parse_folder(
        folder: str | Path,
        *,
        tz: ZoneInfo | None = None,
    ) -> pd.DataFrame:
        ...

The returned DataFrame must include columns matching the ``Result`` model fields.
At minimum: ``source_file``, ``name_id``, ``investigation``, ``result``, ``units``,
``flag``, ``reference_range_lower``, ``reference_range_upper``, and the various
datetime and specimen metadata columns.

Register the parser in ``EDC_LAB_RESULTS_PARSERS``:

.. code-block:: python

    EDC_LAB_RESULTS_PARSERS = {
        "MNH": "parse_trial_labs.parsers.parse_mnh",
        "KCMC": "my_project.parsers.kcmc_parse_folder",
    }

Management Commands
~~~~~~~~~~~~~~~~~~~

``import_labs``
    Parses PDF files, resolves investigation mappings interactively, and saves
    results to the database.

    .. code-block:: bash

        manage.py import_labs /path/to/pdf_folder --laboratory "MNH"
        manage.py import_labs /path/to/pdf_folder --laboratory "MNH" --dry-run
        manage.py import_labs /path/to/pdf_folder --laboratory "MNH" --output results.csv

    The ``--laboratory`` flag is required. It selects the parser from ``EDC_LAB_RESULTS_PARSERS``
    and scopes the investigation mappings in ``InvestigationMapping``.

    On first run, the command prompts for each unknown investigation:

    .. code-block:: text

        Unknown investigation: CHOLESTEROL
          Best guess: chol
          Enter utest_id for 'CHOLESTEROL' [chol] or 'u' for unknown:

    Accepted mappings are saved to ``InvestigationMapping`` and reused on subsequent runs.
    The command also checks ``edc_reportable.NormalData`` and warns about mapped
    ``utest_id`` values that have no normal range data.

``update_mapping``
    Updates an existing mapping and backfills the ``utest_id`` on all matching
    ``Result`` rows.

    .. code-block:: bash

        manage.py update_mapping --laboratory "MNH" \
            --investigation "ABS NEUTROPHIL" --utest-id "neutrophil"

    Checks for conflicts (another investigation already mapped to the same
    ``utest_id``) and refreshes the ``in_reportable`` flag.
