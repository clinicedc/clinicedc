edc-lab-results-import
======================


Importing External Lab Results
------------------------------

``edc_lab_results_import`` imports lab results from external sources (e.g. PDF reports from a hospital laboratory) into the EDC. The module provides the ``ResultImporter`` class  and the ``Result`` model class. The ``ResultImporter`` accesses a folder of PDF lab results.

To fetch PDF attachments from a Gmail account before importing, see the separate ``download-gmail-pdfs`` project.

Run manually ...

.. code-block:: python

    from edc_lab_results_import.result_importer import ResultImporter

    importer = ResultImporter(
        "MNH",
        Path("~/upload/gmail").expanduser(),
        is_valid_identifier_func=is_valid_subject_identifier,
        extra_panels=[wbc_differential],
    )
    importer.run(to_model=True)

or as a management command ...

.. code-block:: bash

    manage.py import_results /path/to/pdf_folder --laboratory "MNH"
    manage.py import_results /path/to/pdf_folder --laboratory "MNH" --dry-run


Settings
~~~~~~~~

``EDC_LAB_RESULTS_PARSERS``
    A dictionary mapping laboratory abbreviations to parser callables.

    .. code-block:: python

        # settings.py

        EDC_LAB_RESULTS_PARSERS = {
            "MNH": "my_project.parsers.parse_mnh_pdf",
        }

``EDC_LAB_RESULTS_MAPPING_FILES``
    A dictionary mapping laboratory abbreviations to the path of a JSON file containing that laboratory's investigation-name-to-``utestid`` and unit mappings.

    .. code-block:: python

        # settings.py

        EDC_LAB_RESULTS_MAPPING_FILES = {
            "MNH": "/path/to/mnh_mappings.json",
        }

    .. code-block:: json

        {
            "MNH": {
                "UTESTIDS": {
                    "Haemoglobin": "hgb",
                    "White Cell Count": "wbc",
                    "Creatinine": "creatinine"
                },
                "UNITS": {
                    "g/dL": "g/dL",
                    "10*3/uL": "10^3/L"
                }
            }
        }

``EDC_LAB_RESULTS_UPLOAD_DIR``
    Checked by a Django system check (``upload_dir_check``) on startup.

Models
~~~~~~

``Result``
    Stores one row per investigation result parsed from a PDF

Writing a Custom Parser
~~~~~~~~~~~~~~~~~~~~~~~

Parsing is delegated to the ``parse_trial_labs`` package's ``parse_folder()``,
which walks every PDF in a directory and calls your registered parser **once per
file** — not once per folder:

.. code-block:: python

    def parse_mnh_pdf(
        pdf_file_path: Path,
        *,
        tz: ZoneInfo | None = None,
        is_valid_identifier_func: Callable | None = None,
    ) -> list[dict]:
        ...

Each call must return a list of row-dicts (one dict per investigation/result on
that PDF); ``parse_folder`` concatenates every file's rows into a single
``pandas.DataFrame``. At minimum each row needs keys matching the ``Result``
source/test-data fields consumed by ``ResultImporter.parse_pdfs_to_dataframe``:
``source_file``, ``name_id``, ``source_utestid``, ``source_units``, ``result``,
``flag``, ``reference_range_lower``, ``reference_range_upper``, ``order_no``,
``order_datetime``, ``result_status``, plus subject/screening identifiers and the
specimen/report datetime columns.

Register the parser in ``EDC_LAB_RESULTS_PARSERS`` as shown above.
